from typing import List
import torch
import numpy as np
import ase
import ase.neighborlist
from ase.db.row import AtomsRow
from src.charge3net.data.layer import pad_and_stack
import math
import multiprocessing
import time
import queue
import logging
from ase.db import connect
from scipy.spatial import KDTree, cKDTree
from scipy.spatial.distance import euclidean


class DensityData(torch.utils.data.Dataset):
    def __init__(self, mysql_url, **kwargs):
        super().__init__(**kwargs)
        db = connect(mysql_url)
        print(f'len db {len(db)}')
        self.data = [i for i in range(1, len(db) + 1)]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]
    



class GraphConstructor(object):
    def __init__(self, cutoff, num_probes=None, disable_pbc=False, sorted_edges=False):
        super().__init__()
        self.cutoff = cutoff
        self.disable_pbc = disable_pbc
        self.sorted_edges = sorted_edges
        self.default_type = torch.get_default_dtype()
        self.num_probes = num_probes

    def __call__(self,
        density,
        atoms,
        grid_pos,
        threshold_distance,
        ):

        if self.disable_pbc:
            atoms = atoms.copy()
            atoms.set_pbc(False)

        probe_pos_valid, probe_target_valid, probe_pos_invalid, probe_target_invalid = self.sample_probes(grid_pos, density, atoms, threshold_distance)

        graph_dict_invalid = self.atoms_and_probes_to_graph(atoms, probe_pos_invalid)
        
        # pylint: disable=E1102
        graph_dict_invalid.update(
            probe_target=torch.tensor(probe_target_invalid, dtype=self.default_type),
            num_nodes=torch.tensor(graph_dict_invalid["nodes"].shape[0]),
            num_atom_edges=torch.tensor(graph_dict_invalid["atom_edges"].shape[0]),
            num_probes=torch.tensor(probe_target_invalid.shape[0]),
            num_probe_edges=torch.tensor(graph_dict_invalid["probe_edges"].shape[0]),
            probe_xyz=torch.tensor(probe_pos_invalid, dtype=self.default_type),
            atom_xyz=torch.tensor(atoms.get_positions(), dtype=self.default_type),
            cell=torch.tensor(np.array(atoms.get_cell()), dtype=self.default_type),
        )

        if len(probe_target_valid) < 1:
            return None, graph_dict_invalid
        else:
            graph_dict_valid = self.atoms_and_probes_to_graph(atoms, probe_pos_valid)
            
            # pylint: disable=E1102
            graph_dict_valid.update(
                probe_target=torch.tensor(probe_target_valid, dtype=self.default_type),
                num_nodes=torch.tensor(graph_dict_valid["nodes"].shape[0]),
                num_atom_edges=torch.tensor(graph_dict_valid["atom_edges"].shape[0]),
                num_probes=torch.tensor(probe_target_valid.shape[0]),
                num_probe_edges=torch.tensor(graph_dict_valid["probe_edges"].shape[0]),
                probe_xyz=torch.tensor(probe_pos_valid, dtype=self.default_type),
                atom_xyz=torch.tensor(atoms.get_positions(), dtype=self.default_type),
                cell=torch.tensor(np.array(atoms.get_cell()), dtype=self.default_type),
            )

            return graph_dict_valid, graph_dict_invalid

    def sample_probes(self, grid_pos, density, atoms, threshold_distance=1.0):
        probe_pos = grid_pos.reshape(-1,3)
        probe_target = density.flatten()
        positions = atoms.positions
        tree = cKDTree(positions)
        valid_indices = []
        invalid_indices = []
        for i, target in enumerate(probe_pos):
            # 查找在给定半径内的原子索引
            indices = tree.query_ball_point(target, threshold_distance)
            if len(indices) > 0:
                valid_indices.append(i)
            else:
                invalid_indices.append(i)
        probe_pos_valid = probe_pos[valid_indices, :]
        probe_target_valid = probe_target[valid_indices]

        probe_pos_invalid = probe_pos[invalid_indices, :]
        probe_target_invalid = probe_target[invalid_indices]

        return probe_pos_valid, probe_target_valid, probe_pos_invalid, probe_target_invalid
    # def sample_probes(self, grid_pos, density):
    #     if self.num_probes is not None:
    #         # # probe_choice_max = np.prod(grid_pos.shape[0:3])
    #         # probe_choice = np.random.randint(grid_pos.shape[0], size=self.num_probes)
    #         # # probe_choice = np.unravel_index(probe_choice, grid_pos.shape[0:3])
    #         # probe_pos = grid_pos[probe_choice]
    #         # probe_target = density[probe_choice]
    #         probe_choice_max = np.prod(grid_pos.shape[0:3])
    #         probe_choice = np.random.randint(probe_choice_max, size=self.num_probes)
    #         probe_choice = np.unravel_index(probe_choice, grid_pos.shape[0:3])
    #         probe_pos = grid_pos[probe_choice]
    #         probe_target = density[probe_choice]            
    #     else:
    #         probe_pos = grid_pos.reshape(-1,3)
    #         if len(density.shape) == 4: # spin density TODO: have actual arg for spin
    #             probe_target = density.reshape(-1, 2)
    #         else:
    #             probe_target = density.flatten()
    #     return probe_pos, probe_target

    
    def atoms_and_probes_to_graph(self, atoms, probe_pos):
        atom_edges, atom_edges_displacement, neighborlist, inv_cell_T = self.atoms_to_graph(atoms)
        
        probe_edges, probe_edges_displacement = self.probes_to_graph(atoms, probe_pos, 
            neighborlist=neighborlist, inv_cell_T=inv_cell_T)        

        if self.sorted_edges:
            # Sort probe edges for reproducibility
            concat_pe = _sort_by_rows(np.concatenate((probe_edges, probe_edges_displacement), axis=1))
            probe_edges = concat_pe[:,:2].astype(int)
            probe_edges_displacement = concat_pe[:,2:]

        graph_dict = {
            "nodes": torch.tensor(atoms.get_atomic_numbers()),
            "atom_edges": torch.tensor(np.concatenate(atom_edges, axis=0)),
            "atom_edges_displacement": torch.tensor(
                np.concatenate(atom_edges_displacement, axis=0), dtype=self.default_type
            ),
            "probe_edges": torch.tensor(probe_edges),
            "probe_edges_displacement": torch.tensor(
                probe_edges_displacement, dtype=self.default_type
            ),
        }
        return graph_dict

    def atoms_to_graph(self, atoms):
        atom_edges = []
        atom_edges_displacement = []

        inv_cell_T = np.linalg.inv(atoms.get_cell().complete().T)

        # Compute neighborlist
        if (
            True # force ASE
            or np.any(atoms.get_cell().lengths() <= 0.0001)
            or (
                np.any(atoms.get_pbc())
                and np.any(_cell_heights(atoms.get_cell()) < self.cutoff)
            )
        ):
            neighborlist = AseNeigborListWrapper(self.cutoff, atoms)
        else:
            # neighborlist = AseNeigborListWrapper(cutoff, atoms)
            neighborlist = asap3.FullNeighborList(self.cutoff, atoms)

        atom_positions = atoms.get_positions()

        for i in range(len(atoms)):
            neigh_idx, neigh_vec, _ = neighborlist.get_neighbors(i, self.cutoff)

            self_index = np.ones_like(neigh_idx) * i
            edges = np.stack((neigh_idx, self_index), axis=1)

            neigh_pos = atom_positions[neigh_idx]
            this_pos = atom_positions[i]
            neigh_origin = neigh_vec + this_pos - neigh_pos
            neigh_origin_scaled = np.round(inv_cell_T.dot(neigh_origin.T).T)

            atom_edges.append(edges)
            atom_edges_displacement.append(neigh_origin_scaled)

        return atom_edges, atom_edges_displacement, neighborlist, inv_cell_T

    def probes_to_graph(self, atoms, probe_pos, neighborlist=None, inv_cell_T=None):
        # FIXME: can turn this into atoms_and_probes_to_graph. The atoms NNs can be extracted
        # from the KD tree. This will circumvent ASAP/Ase completely
        atom_positions = atoms.positions
        atom_idx = np.arange(len(atoms))

        if inv_cell_T is None:
            inv_cell_T = np.linalg.inv(atoms.get_cell().complete().T)

        # get number of repeats in each dimension
        pbc = atoms.get_pbc()
        cell_heights = _cell_heights(atoms.get_cell())
        n_rep = np.ceil(self.cutoff / (cell_heights + 1e-12))
        _rep = lambda dim: np.arange(-n_rep[dim], n_rep[dim] + 1) if pbc[dim] else [0]
        repeat_offsets = np.array([(x, y, z) for x in _rep(0) for y in _rep(1) for z in _rep(2)])

        # total repeats in all dimensions
        total_repeats = repeat_offsets.shape[0]
        # project repeat cell offsets into cartesian space
        repeat_offsets = np.dot(repeat_offsets, atoms.get_cell())
        # tile grid positions, subtract offsets 
        # (subtracting grid positions is like adding atom positions)
        supercell_atom_pos = np.repeat(atom_positions[..., None, :], total_repeats, axis=-2)
        supercell_atom_pos += repeat_offsets
        
        # store the original index of each atom
        supercell_atom_idx = np.repeat(atom_idx[:, None], total_repeats, axis=-1)

        # flatten
        supercell_atom_positions = supercell_atom_pos.reshape(np.prod(supercell_atom_pos.shape[:2]), 3)
        supercell_atom_idx = supercell_atom_idx.reshape(np.prod(supercell_atom_pos.shape[:2]))

        # create KDTrees for atoms and probes
        atom_kdtree = KDTree(supercell_atom_positions)
        probe_kdtree = KDTree(probe_pos)

        # query points between kd tree
        query = probe_kdtree.query_ball_tree(atom_kdtree, r=self.cutoff)

        # set up vector of destination nodes (probes)
        edges_per_probe = [len(q) for q in query]
        dest_node_idx = np.concatenate([[i]*n for i,n in enumerate(edges_per_probe)]).astype(int)

        # get original atom idx from supercell idx
        supercell_neigh_idx = np.concatenate(query).astype(int)
        src_node_idx = supercell_atom_idx[supercell_neigh_idx]
        # create edges from src/dest nodes
        probe_edges = np.stack((src_node_idx, dest_node_idx), axis=1)

        # get non-supercell atom positions
        src_pos = atom_positions[src_node_idx]
        dest_pos = probe_pos[dest_node_idx]

        # FIXME: on the next two lines, what is the purpose of dest_pos? 
        # edge vector between supercell atoms and probe
        neigh_vecs = supercell_atom_positions[supercell_neigh_idx] - dest_pos
        # compute displacement (number of unitcells in each dim)
        neigh_origin = neigh_vecs + dest_pos - src_pos
        probe_edges_displacement = np.round(inv_cell_T.dot(neigh_origin.T).T)

        return probe_edges, probe_edges_displacement

# class KdTreeGraphConstructor(GraphConstructor):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def probes_to_graph(self, atoms, probe_pos, neighborlist=None, inv_cell_T=None):
#         # FIXME: can turn this into atoms_and_probes_to_graph. The atoms NNs can be extracted
#         # from the KD tree. This will circumvent ASAP/Ase completely
#         atom_positions = atoms.positions
#         atom_idx = np.arange(len(atoms))

#         if inv_cell_T is None:
#             inv_cell_T = np.linalg.inv(atoms.get_cell().complete().T)

#         # get number of repeats in each dimension
#         pbc = atoms.get_pbc()
#         cell_heights = _cell_heights(atoms.get_cell())
#         n_rep = np.ceil(self.cutoff / (cell_heights + 1e-12))
#         _rep = lambda dim: np.arange(-n_rep[dim], n_rep[dim] + 1) if pbc[dim] else [0]
#         repeat_offsets = np.array([(x, y, z) for x in _rep(0) for y in _rep(1) for z in _rep(2)])

#         # total repeats in all dimensions
#         total_repeats = repeat_offsets.shape[0]
#         # project repeat cell offsets into cartesian space
#         repeat_offsets = np.dot(repeat_offsets, atoms.get_cell())
#         # tile grid positions, subtract offsets 
#         # (subtracting grid positions is like adding atom positions)
#         supercell_atom_pos = np.repeat(atom_positions[..., None, :], total_repeats, axis=-2)
#         supercell_atom_pos += repeat_offsets
        
#         # store the original index of each atom
#         supercell_atom_idx = np.repeat(atom_idx[:, None], total_repeats, axis=-1)

#         # flatten
#         supercell_atom_positions = supercell_atom_pos.reshape(np.prod(supercell_atom_pos.shape[:2]), 3)
#         supercell_atom_idx = supercell_atom_idx.reshape(np.prod(supercell_atom_pos.shape[:2]))

#         # create KDTrees for atoms and probes
#         atom_kdtree = KDTree(supercell_atom_positions)
#         probe_kdtree = KDTree(probe_pos)

#         # query points between kd tree
#         query = probe_kdtree.query_ball_tree(atom_kdtree, r=self.cutoff)

#         # set up vector of destination nodes (probes)
#         edges_per_probe = [len(q) for q in query]
#         dest_node_idx = np.concatenate([[i]*n for i,n in enumerate(edges_per_probe)]).astype(int)

#         # get original atom idx from supercell idx
#         supercell_neigh_idx = np.concatenate(query).astype(int)
#         src_node_idx = supercell_atom_idx[supercell_neigh_idx]
#         # create edges from src/dest nodes
#         probe_edges = np.stack((src_node_idx, dest_node_idx), axis=1)

#         # get non-supercell atom positions
#         src_pos = atom_positions[src_node_idx]
#         dest_pos = probe_pos[dest_node_idx]

#         # FIXME: on the next two lines, what is the purpose of dest_pos? 
#         # edge vector between supercell atoms and probe
#         neigh_vecs = supercell_atom_positions[supercell_neigh_idx] - dest_pos
#         # compute displacement (number of unitcells in each dim)
#         neigh_origin = neigh_vecs + dest_pos - src_pos
#         probe_edges_displacement = np.round(inv_cell_T.dot(neigh_origin.T).T)

#         return probe_edges, probe_edges_displacement

class AseNeigborListWrapper:
    """
    Wrapper around ASE neighborlist to have the same interface as asap3 neighborlist

    """

    def __init__(self, cutoff, atoms):
        self.neighborlist = ase.neighborlist.NewPrimitiveNeighborList(
            cutoff, skin=0.0, self_interaction=False, bothways=True
        )
        self.neighborlist.build(
            atoms.get_pbc(), atoms.get_cell(), atoms.get_positions()
        )
        self.cutoff = cutoff
        self.atoms_positions = atoms.get_positions()
        self.atoms_cell = atoms.get_cell()

    def get_neighbors(self, i, cutoff):
        assert (
            cutoff == self.cutoff
        ), "Cutoff must be the same as used to initialise the neighborlist"

        indices, offsets = self.neighborlist.get_neighbors(i)

        rel_positions = (
            self.atoms_positions[indices]
            + offsets @ self.atoms_cell
            - self.atoms_positions[i][None]
        )

        dist2 = np.sum(np.square(rel_positions), axis=1)
        return indices, rel_positions, dist2

def _cell_heights(cell_object):
    volume = cell_object.volume
    crossproducts = np.cross(cell_object[[1, 2, 0]], cell_object[[2, 0, 1]])
    crosslengths = np.sqrt(np.sum(np.square(crossproducts), axis=1))
    heights = volume / crosslengths
    return heights

def _sort_by_rows(arr):
    assert len(arr.shape) == 2, "Only 2D arrays"
    return np.array(sorted([tuple(x) for x in arr.tolist()]))





class MyCollator(object):
    def __init__(self, mysql_url, cutoff=4.0, num_probes=None):
        self.mysql_url = mysql_url
        self.graph_constructor = GraphConstructor(cutoff=cutoff, num_probes=num_probes)
        
    def __call__(self, examples):
        # ind_examples = sorted(range(len(examples)), key=lambda k: examples[k])

        rows = query_database(self.mysql_url, examples)
        

        list_of_dicts = []
        list_of_dicts_invalid = []
        for row in rows:
            atoms = row.toatoms()
            atoms.set_pbc(True)
            nx, ny, nz = row.data['nx'], row.data['ny'], row.data['nz']
            probe_pos = get_grid_centers(atoms, nx, ny, nz)
            # density = row.data['chg']
            density = row.data['chg'].reshape(nx, ny, nz)
            
            num_positions = nx * ny * nz
            batch_size = 3000
            threshold_distance = 0.1
            for start_idx in range(0, num_positions, batch_size):
                end_idx = min(start_idx + batch_size, num_positions)

                
                unravel_indices = np.unravel_index(np.arange(start_idx, end_idx), (nx, ny, nz))
                # 使用三维索引提取 probe_pos 和 density
                probe_pos_batch = probe_pos[unravel_indices]
                density_batch = density[unravel_indices]
                
                probe_pos_chosen, probe_target_chosen, _, _ = self.graph_constructor.sample_probes(probe_pos_batch, density_batch, atoms, threshold_distance=threshold_distance)
                
                graph_dict, graph_dict_invalid = self.graph_constructor.__call__(density=density_batch, atoms=atoms, grid_pos=probe_pos_batch, threshold_distance=threshold_distance)
                
                list_of_dicts_invalid.append(collate_list_of_dicts([graph_dict_invalid]))
                #print(len(probe_target_chosen))
                if len(probe_target_chosen) < 2:
                    continue
                # 构造图字典

                graph_dict = res_input_constructor(atoms=atoms, 
                                                   grid_pos=probe_pos_chosen, 
                                                   graph_dict=graph_dict, 
                                                   threshold_distance=threshold_distance)

                # 将分批处理的结果添加到列表中
                list_of_dicts.append(collate_list_of_dicts([graph_dict]))
            

        return list_of_dicts, list_of_dicts_invalid




def res_input_constructor(atoms, grid_pos, graph_dict, threshold_distance):
    positions = atoms.positions
    tree = cKDTree(positions)
    chemical_symbols = atoms.get_atomic_numbers()
    atom_inputs = []
    num_atom_inputs = []
    distances_list = []
    for i, target in enumerate(grid_pos):
        # 查找在给定半径内的原子索引
        indices = tree.query_ball_point(target, threshold_distance)
        distances = torch.tensor([euclidean(target, positions[index]) for index in indices])
        atom_chem = torch.tensor([chemical_symbols[item] for item in indices])
        # atom_indx = torch.tensor(indices)

        distances_list.append(distances)
        num_atoms = len(indices)
        atom_inputs.append(atom_chem)
        # atom_inputs.append(atom_indx)
        num_atom_inputs.append(num_atoms)
    
    graph_dict.update(
        neighbour_atom=torch.cat(atom_inputs, dim=0).long(),
        num_neighbour_atoms=torch.tensor(num_atom_inputs).long(),
        distances=torch.cat(distances_list, dim=0).float()
        )
    return graph_dict


def collate_list_of_dicts(list_of_dicts, pin_memory=False):
    # Convert from "list of dicts" to "dict of lists"
    dict_of_lists = {k: [d[k] for d in list_of_dicts] for k in list_of_dicts[0]}

    # Convert each list of tensors to single tensor with pad and stack
    if pin_memory:
        pin = lambda x: x.pin_memory()
    else:
        pin = lambda x: x

    collated = {}
    for k,v  in dict_of_lists.items():
        if not k in ["filename", 
                     "load_time", 
                     'num_neighbour_atoms',
                     'distances',
                     'neighbour_atom']:
            collated[k] = pin(pad_and_stack(v))
        else:
            collated[k] = torch.cat(v, dim=0)

    # collated = {k: pin(pad_and_stack(dict_of_lists[k])) for k in dict_of_lists}
    return collated



def get_grid_centers(atoms, nx, ny, nz):
    """
    Read atoms and cell information from a VASP file and generate Cartesian coordinates of the grid center points.

    Parameters:
    filename (str): File name, VASP file containing cell information (such as POSCAR).
    nx, ny, nz (int): Number of grid divisions.

    Returns:
    np.ndarray: Cartesian coordinate array of grid center points, shape (nx*ny*nz, 3).
    """
    # cell = atoms.get_cell()
    # a, b, c = cell[0], cell[1], cell[2]
    # a_len = np.linalg.norm(a)
    # b_len = np.linalg.norm(b)
    # c_len = np.linalg.norm(c)
    # alpha = np.arccos(np.dot(b, c) / (b_len * c_len))
    # beta = np.arccos(np.dot(a, c) / (a_len * c_len))
    # gamma = np.arccos(np.dot(a, b) / (a_len * b_len))
    
    # cos_alpha, cos_beta, cos_gamma = np.cos(alpha), np.cos(beta), np.cos(gamma)
    # sin_gamma = np.sin(gamma)
    
    # volume = a_len * b_len * c_len * np.sqrt(1 - cos_alpha**2 - cos_beta**2 - cos_gamma**2 
    #                                          + 2 * cos_alpha * cos_beta * cos_gamma)
    # cell_matrix = np.array([
    #     [a_len, b_len * cos_gamma, c_len * cos_beta],
    #     [0, b_len * sin_gamma, c_len * (cos_alpha - cos_beta * cos_gamma) / sin_gamma],
    #     [0, 0, volume / (a_len * b_len * sin_gamma)]
    # ])
    
    # fractional_coords = np.array([[(i + 0.5) / nx, (j + 0.5) / ny, (k + 0.5) / nz] for i in range(nx) for j in range(ny) for k in range(nz)])
    # cartesian_coords = np.dot(fractional_coords, cell_matrix.T).reshape(nx, ny, nz, 3)
    # grid_pos = cartesian_coords

    ngridpts = np.array([nx, ny, nz])  # grid matrix
    grid_pos = np.meshgrid(
        np.arange(ngridpts[0]) / nx,
        np.arange(ngridpts[1]) / ny,
        np.arange(ngridpts[2]) / nz,
        indexing="ij",
    )
    grid_pos = np.stack(grid_pos, 3)
    grid_pos = np.dot(grid_pos, atoms.get_cell())
    grid_pos = grid_pos

    
    return np.array(grid_pos)



def query_database(mysql_url, idx_list):
    if "db" in str(mysql_url):
        db = connect(mysql_url)
        rows = []
        for idx in idx_list:
            #print(idx)
            it = db.get(id=idx)
            rows.append(it)
        return rows
    
    
    else:
        count = 0
        while True:
            try:
                db = connect(mysql_url)
                con = db._connect().cursor()

                
                input = {}
                cmps = [('id', ' IN ', '1,2')]

                keys = []  # No additional keys are needed for a simple ID query
                sort = None  # Assuming no sorting is required
                order = None  # Default order, can be 'DESC' for descending
                sort_table = None  # Not needed for an ID query
                columns = 'all'  # If you want all columns, otherwise specify the columns you need

                values = np.array([None for i in range(27)])
                values[25] = '{}'
                columnindex = list(range(27))

                what = ', '.join('systems.' + name
                                    for name in
                                    np.array(db.columnnames)[np.array(columnindex)])


                sql, args = db.create_select_statement(keys, cmps, sort, order,
                                                            sort_table, what)

                args = [tuple(idx_list)]


                con.execute(sql, args)

                deblob = db.deblob
                decode = db.decode

                rows = []

                for shortvalues in con.fetchall():
                    values[columnindex] = shortvalues
                    dct = {'id': values[0],
                                'unique_id': values[1],
                                'ctime': values[2],
                                'mtime': values[3],
                                'user': values[4],
                                'numbers': deblob(values[5], np.int32),
                                'positions': deblob(values[6], shape=(-1, 3)),
                                'cell': deblob(values[7], shape=(3, 3))}

                    # if values[8] is not None:
                    #     dct['pbc'] = (values[8] & np.array([1, 2, 4])).astype(bool)
                    # if values[9] is not None:
                    #     dct['initial_magmoms'] = deblob(values[9])
                    # if values[10] is not None:
                    #     dct['initial_charges'] = deblob(values[10])
                    # if values[11] is not None:
                    #     dct['masses'] = deblob(values[11])
                    # if values[12] is not None:
                    #     dct['tags'] = deblob(values[12], np.int32)
                    # if values[13] is not None:
                    #     dct['momenta'] = deblob(values[13], shape=(-1, 3))
                    # if values[14] is not None:
                    #     dct['constraints'] = values[14]
                    # if values[15] is not None:
                    #     dct['calculator'] = values[15]
                    # if values[16] is not None:
                    #     dct['calculator_parameters'] = decode(values[16])
                    # if values[17] is not None:
                    #     dct['energy'] = values[17]
                    # if values[18] is not None:
                    #     dct['free_energy'] = values[18]
                    # if values[19] is not None:
                    #     dct['forces'] = deblob(values[19], shape=(-1, 3))
                    # if values[20] is not None:
                    #     dct['stress'] = deblob(values[20])
                    # if values[21] is not None:
                    #     dct['dipole'] = deblob(values[21])
                    # if values[22] is not None:
                    #     dct['magmoms'] = deblob(values[22])
                    # if values[23] is not None:
                    #     dct['magmom'] = values[23]
                    # if values[24] is not None:
                    #     dct['charges'] = deblob(values[24])
                    # if values[25] != '{}':
                    #     dct['key_value_pairs'] = decode(values[25])
                    if len(values) >= 27 and values[26] != 'null':
                        dct['data'] = decode(values[26], lazy=True)
                    
                    # external_tab = db._get_external_table_names()
                    # tables = {}
                    # for tab in external_tab:
                    #     row = self._read_external_table(tab, dct["id"])
                    #     tables[tab] = row

                    # dct.update(tables)
                    rows.append(AtomsRow(dct))
                return rows
            except Exception as e:
                time.sleep(1)  # 等待一秒再重试
                count += 1
                print(f"trying {count} times")
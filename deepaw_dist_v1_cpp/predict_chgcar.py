#!/usr/bin/env python
"""
HfO2 Complete CHGCAR Prediction - Using Encrypted Models
Predicts full charge density grid and writes VASP CHGCAR file
"""
import numpy as np
import torch
from ase.db import connect
from ase.calculators.vasp import VaspChargeDensity
from pathlib import Path
from tqdm import tqdm

# Import deepaw package
from deepaw import SecureModel
from deepaw.data.graph_construction import KdTreeGraphConstructor
from deepaw.data.collate import collate_list_of_dicts

# Fixed batch size for the encrypted model
FIXED_BATCH_SIZE = 1000

def move_to_device(obj, device):
    """Recursively move data to device"""
    if isinstance(obj, torch.Tensor):
        return obj.to(device)
    elif isinstance(obj, dict):
        return {k: move_to_device(v, device) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [move_to_device(item, device) for item in obj]
    return obj

def predict_batch(atoms, probe_positions, model, graph_constructor, device):
    """Predict single batch (100 probe points)"""
    assert len(probe_positions) == FIXED_BATCH_SIZE

    # Build graph data
    dummy_density = np.zeros(FIXED_BATCH_SIZE)
    temp_grid_pos = probe_positions.reshape(FIXED_BATCH_SIZE, 1, 1, 3)
    temp_density = dummy_density.reshape(FIXED_BATCH_SIZE, 1, 1)

    graph_dict = graph_constructor(temp_density, atoms, temp_grid_pos)
    batch = collate_list_of_dicts([graph_dict], pin_memory=False)
    batch = move_to_device(batch, device)

    # Predict
    predictions, _ = model(batch)
    return predictions.cpu().numpy()

def predict_full_grid(atoms, model, graph_constructor, device, nx=40, ny=40, nz=40):
    """
    Predict charge density on full 3D grid

    Args:
        atoms: ASE Atoms object
        model: SecureModel instance
        graph_constructor: KdTreeGraphConstructor instance
        device: 'cuda' or 'cpu'
        nx, ny, nz: Grid dimensions

    Returns:
        density: (nx*ny*nz,) array of predicted densities
    """
    print(f"\nGenerating {nx}x{ny}x{nz} grid ({nx*ny*nz} total points)...")

    # Generate full grid in fractional coordinates
    x = np.linspace(0, 1, nx, endpoint=False)
    y = np.linspace(0, 1, ny, endpoint=False)
    z = np.linspace(0, 1, nz, endpoint=False)

    xv, yv, zv = np.meshgrid(x, y, z, indexing='ij')
    frac_coords = np.stack([xv.ravel(), yv.ravel(), zv.ravel()], axis=1)

    # Convert to Cartesian coordinates
    cell = atoms.get_cell()
    probe_positions = np.dot(frac_coords, cell)

    total_probes = len(probe_positions)
    print(f"Total probe points: {total_probes}")

    # Split into batches of 100
    num_batches = (total_probes + FIXED_BATCH_SIZE - 1) // FIXED_BATCH_SIZE
    print(f"Processing in {num_batches} batches of {FIXED_BATCH_SIZE}...")

    all_predictions = []

    for i in tqdm(range(num_batches), desc="Predicting batches"):
        start_idx = i * FIXED_BATCH_SIZE
        end_idx = min((i + 1) * FIXED_BATCH_SIZE, total_probes)
        batch_probes = probe_positions[start_idx:end_idx]

        # Pad if necessary
        if len(batch_probes) < FIXED_BATCH_SIZE:
            pad_size = FIXED_BATCH_SIZE - len(batch_probes)
            last_probe = batch_probes[-1:].repeat(pad_size, axis=0)
            padded_probes = np.vstack([batch_probes, last_probe])

            # Predict and remove padding
            batch_pred = predict_batch(atoms, padded_probes, model, graph_constructor, device)
            batch_pred = batch_pred[:len(batch_probes)]
        else:
            batch_pred = predict_batch(atoms, batch_probes, model, graph_constructor, device)

        all_predictions.append(batch_pred)

    # Concatenate all predictions
    density = np.concatenate(all_predictions, axis=0)

    return density


def write_chgcar(density, atoms, nx, ny, nz, output_path):
    """
    Write charge density to VASP CHGCAR format using ASE

    Args:
        density: (nx*ny*nz,) array of densities
        atoms: ASE Atoms object (will be cleaned)
        nx, ny, nz: Grid dimensions
        output_path: Output file path
    """
    print(f"\nWriting CHGCAR file...")

    # Reshape density to 3D grid
    charge_grid = density.reshape(nx, ny, nz)

    # Clean atoms object - remove momentum and constants
    # Create a clean copy without unnecessary data
    clean_atoms = atoms.copy()

    # Remove momentum if present
    if clean_atoms.has('momenta'):
        del clean_atoms.arrays['momenta']

    # Remove any constraint data
    clean_atoms.constraints = []

    # Create VaspChargeDensity object
    vcd = VaspChargeDensity(filename=None)
    vcd.atoms.append(clean_atoms)
    vcd.chg.append(charge_grid)

    # Write CHGCAR file
    vcd.write(output_path, format="chgcar")
    print(f"✓ CHGCAR saved to: {output_path}")


def main():
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Predict CHGCAR from ASE database')
    parser.add_argument('--db', type=str, default='tests/hfo2.db', help='Path to ASE database file')
    parser.add_argument('--id', type=int, default=1, help='Structure ID in database')
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu',
                        choices=['cuda', 'cpu'], help='Device to use (cuda or cpu)')
    parser.add_argument('--grid', type=int, nargs=3, default=[40, 40, 40],
                        help='Grid dimensions (nx ny nz)')
    parser.add_argument('--output', type=str, default=None, help='Output CHGCAR file path')

    args = parser.parse_args()

    print("=" * 70)
    print("HfO2 Complete CHGCAR Prediction - Encrypted Model Version")
    print("=" * 70)

    # Configuration from arguments
    DB_PATH = args.db
    STRUCTURE_ID = args.id
    DEVICE = args.device

    # Grid dimensions
    NX, NY, NZ = args.grid

    # Output path
    if args.output is None:
        OUTPUT_PATH = f'CHGCAR_id{STRUCTURE_ID}'
    else:
        OUTPUT_PATH = args.output

    # 1. Load structure
    print(f"\n1. Loading structure (ID={STRUCTURE_ID})...")
    db = connect(DB_PATH)
    atoms = None
    for row in db.select(id=STRUCTURE_ID):
        atoms = row.toatoms()
        break

    print(f"   Formula: {atoms.get_chemical_formula()}")
    print(f"   Number of atoms: {len(atoms)}")
    print(f"   Cell: {atoms.get_cell().cellpar()}")

    # 2. Load encrypted model
    print(f"\n2. Loading encrypted model (device: {DEVICE})...")
    model = SecureModel(device=DEVICE)

    if DEVICE == 'cuda':
        print(f"   GPU: {torch.cuda.get_device_name(0)}")

    # 3. Predict full grid
    print(f"\n3. Predicting full charge density grid...")
    graph_constructor = KdTreeGraphConstructor(cutoff=4.0, disable_pbc=False)
    density = predict_full_grid(atoms, model, graph_constructor, DEVICE, NX, NY, NZ)

    # 4. Output statistics
    print(f"\n4. Prediction results:")
    print(f"   Grid dimensions: {NX}x{NY}x{NZ}")
    print(f"   Total points: {len(density)}")
    print(f"   Density statistics:")
    print(f"     Min: {density.min():.6f}")
    print(f"     Max: {density.max():.6f}")
    print(f"     Mean: {density.mean():.6f}")
    print(f"     Std: {density.std():.6f}")

    # 5. Write CHGCAR file
    print(f"\n5. Writing CHGCAR file...")
    write_chgcar(density, atoms, NX, NY, NZ, OUTPUT_PATH)

    print("\n" + "=" * 70)
    print("✓ CHGCAR prediction completed!")
    print(f"✓ Output file: {OUTPUT_PATH}")
    print("=" * 70)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Hemilineage Status Reset Utility with Separate Status Tracking

This script allows you to reset the status of hemilineages in the summary file
for both whole neuron and CBF processing separately.

Status codes:
- 0: Not started
- 1: Completed
- -1: Error

Usage:
    python reset_status_v2.py [options]

Examples:
    python reset_status_v2.py --all_wn_to 0                         # Reset all whole neuron to "not started"
    python reset_status_v2.py --all_cbf_to 0                        # Reset all CBF to "not started"
    python reset_status_v2.py --batch 0 --wn_to 0 --cbf_to 0       # Reset batch 0 both types to "not started"
    python reset_status_v2.py --hemilineage FLAa2 --wn_to 0        # Reset FLAa2 whole neuron to "not started"
    python reset_status_v2.py --errors_to 0                        # Reset all errors to "not started"
"""

import argparse
import pandas as pd
import sys
from datetime import datetime


def load_summary(csv_file='hemileage_summary.csv'):
    """Load the hemileage summary from CSV file."""
    try:
        df = pd.read_csv(csv_file)
        
        # Check if required columns exist
        required_columns = ['status_whole_neuron', 'status_cbf']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Error: Missing required columns in CSV: {missing_columns}")
            print("Expected columns: status_whole_neuron, status_cbf")
            sys.exit(1)
        
        return df
    except FileNotFoundError:
        print(f"Error: CSV file {csv_file} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        sys.exit(1)


def save_summary(df, csv_file='hemileage_summary.csv'):
    """Save the updated hemileage summary back to CSV file."""
    try:
        # Create backup
        backup_file = f"{csv_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        original_df = pd.read_csv(csv_file)
        original_df.to_csv(backup_file, index=False)
        print(f"Created backup: {backup_file}")
        
        # Save updated file
        df.to_csv(csv_file, index=False)
        print(f"Updated {csv_file}")
        return True
    except Exception as e:
        print(f"Error saving CSV file: {e}")
        return False


def reset_all_status(df, new_wn_status=None, new_cbf_status=None):
    """Reset status for all hemilineages."""
    if new_wn_status is not None:
        old_wn_counts = df['status_whole_neuron'].value_counts().sort_index()
        df['status_whole_neuron'] = new_wn_status
        print(f"Reset all {len(df)} hemilineages whole neuron status to {new_wn_status}")
        print("Previous whole neuron status distribution:")
        for status, count in old_wn_counts.items():
            print(f"  Status {status}: {count}")
    
    if new_cbf_status is not None:
        old_cbf_counts = df['status_cbf'].value_counts().sort_index()
        df['status_cbf'] = new_cbf_status
        print(f"Reset all {len(df)} hemilineages CBF status to {new_cbf_status}")
        print("Previous CBF status distribution:")
        for status, count in old_cbf_counts.items():
            print(f"  Status {status}: {count}")
    
    return df


def reset_batch_status(df, batch_number, new_wn_status=None, new_cbf_status=None):
    """Reset status for a specific batch."""
    mask = df['batches'] == batch_number
    batch_df = df[mask]
    
    if len(batch_df) == 0:
        print(f"No hemilineages found for batch {batch_number}")
        return df
    
    if new_wn_status is not None:
        old_wn_counts = batch_df['status_whole_neuron'].value_counts().sort_index()
        df.loc[mask, 'status_whole_neuron'] = new_wn_status
        print(f"Reset {len(batch_df)} hemilineages in batch {batch_number} whole neuron status to {new_wn_status}")
        print("Previous whole neuron status distribution for this batch:")
        for status, count in old_wn_counts.items():
            print(f"  Status {status}: {count}")
    
    if new_cbf_status is not None:
        old_cbf_counts = batch_df['status_cbf'].value_counts().sort_index()
        df.loc[mask, 'status_cbf'] = new_cbf_status
        print(f"Reset {len(batch_df)} hemilineages in batch {batch_number} CBF status to {new_cbf_status}")
        print("Previous CBF status distribution for this batch:")
        for status, count in old_cbf_counts.items():
            print(f"  Status {status}: {count}")
    
    return df


def reset_hemilineage_status(df, hemilineage, new_wn_status=None, new_cbf_status=None):
    """Reset status for a specific hemilineage."""
    mask = df['ito_lee_hemilineage'] == hemilineage
    
    if not mask.any():
        print(f"Hemilineage '{hemilineage}' not found")
        return df
    
    if new_wn_status is not None:
        old_wn_status = df.loc[mask, 'status_whole_neuron'].iloc[0]
        df.loc[mask, 'status_whole_neuron'] = new_wn_status
        print(f"Reset {hemilineage} whole neuron status from {old_wn_status} to {new_wn_status}")
    
    if new_cbf_status is not None:
        old_cbf_status = df.loc[mask, 'status_cbf'].iloc[0]
        df.loc[mask, 'status_cbf'] = new_cbf_status
        print(f"Reset {hemilineage} CBF status from {old_cbf_status} to {new_cbf_status}")
    
    return df


def reset_error_status(df, new_status):
    """Reset all hemilineages with status -1 (error) to new status."""
    wn_errors = df['status_whole_neuron'] == -1
    cbf_errors = df['status_cbf'] == -1
    
    wn_error_count = wn_errors.sum()
    cbf_error_count = cbf_errors.sum()
    
    if wn_error_count == 0 and cbf_error_count == 0:
        print("No hemilineages currently have status -1 (error)")
        return df
    
    if wn_error_count > 0:
        df.loc[wn_errors, 'status_whole_neuron'] = new_status
        print(f"Reset {wn_error_count} hemilineages from whole neuron error status to {new_status}")
        error_df = df[wn_errors]
        print("Reset whole neuron error hemilineages:")
        for _, row in error_df.iterrows():
            print(f"  - {row['ito_lee_hemilineage']} (batch {row['batches']})")
    
    if cbf_error_count > 0:
        df.loc[cbf_errors, 'status_cbf'] = new_status
        print(f"Reset {cbf_error_count} hemilineages from CBF error status to {new_status}")
        error_df = df[cbf_errors]
        print("Reset CBF error hemilineages:")
        for _, row in error_df.iterrows():
            print(f"  - {row['ito_lee_hemilineage']} (batch {row['batches']})")
    
    return df


def main():
    """Main function to reset hemilineage status."""
    parser = argparse.ArgumentParser(description='Reset hemilineage processing status with separate tracking')
    
    parser.add_argument('--csv', default='hemileage_summary.csv', 
                       help='Path to hemileage summary CSV file (default: hemileage_summary.csv)')
    
    # Reset all options
    parser.add_argument('--all_wn_to', type=int, choices=[-1, 0, 1],
                       help='Reset all whole neuron statuses to specified value')
    parser.add_argument('--all_cbf_to', type=int, choices=[-1, 0, 1],
                       help='Reset all CBF statuses to specified value')
    
    # Reset by batch
    parser.add_argument('--batch', type=int,
                       help='Batch number to reset (use with --wn_to and/or --cbf_to)')
    parser.add_argument('--wn_to', type=int, choices=[-1, 0, 1],
                       help='New whole neuron status value')
    parser.add_argument('--cbf_to', type=int, choices=[-1, 0, 1],
                       help='New CBF status value')
    
    # Reset by hemilineage
    parser.add_argument('--hemilineage', type=str,
                       help='Specific hemilineage to reset (use with --wn_to and/or --cbf_to)')
    
    # Reset errors
    parser.add_argument('--errors_to', type=int, choices=[-1, 0, 1],
                       help='Reset all error statuses (-1) to specified value')
    
    parser.add_argument('--dry_run', action='store_true',
                       help='Show what would be changed without making changes')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.all_wn_to is not None, args.all_cbf_to is not None, 
                args.batch is not None, args.hemilineage is not None, 
                args.errors_to is not None]):
        print("Error: Must specify one reset operation")
        sys.exit(1)
    
    if (args.batch is not None or args.hemilineage is not None) and \
       (args.wn_to is None and args.cbf_to is None):
        print("Error: Must specify --wn_to and/or --cbf_to when using --batch or --hemilineage")
        sys.exit(1)
    
    # Load data
    df = load_summary(args.csv)
    
    if args.dry_run:
        print("DRY RUN - No changes will be made")
        print()
    
    # Apply reset operation
    if args.all_wn_to is not None or args.all_cbf_to is not None:
        df = reset_all_status(df, args.all_wn_to, args.all_cbf_to)
    elif args.errors_to is not None:
        df = reset_error_status(df, args.errors_to)
    elif args.batch is not None:
        df = reset_batch_status(df, args.batch, args.wn_to, args.cbf_to)
    elif args.hemilineage is not None:
        df = reset_hemilineage_status(df, args.hemilineage, args.wn_to, args.cbf_to)
    
    # Save changes
    if not args.dry_run:
        success = save_summary(df, args.csv)
        if not success:
            sys.exit(1)
    else:
        print("\nDRY RUN - No changes were made")


if __name__ == '__main__':
    main()

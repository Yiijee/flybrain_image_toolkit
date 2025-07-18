#!/usr/bin/env python3
"""
Individual Hemilineage Processor with Separate Status Tracking

This script processes a single hemilineage and updates its status in the hemileage_summary.csv file.

Status codes:
- 0: Not started
- 1: Completed
- -1: Error

Usage:
    python process_single_v2.py <hemilineage_name> [options]

Example:
    python process_single_v2.py FLAa2 --whole_neuron --cbf --downsampling_factor 10
"""

import argparse
import logging
import sys
from process_batch_v2 import HemilineageBatchProcessorV2

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hemilineage_processing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main function to process a single hemilineage."""
    parser = argparse.ArgumentParser(description='Process a single hemilineage with separate status tracking')
    
    parser.add_argument('hemilineage', type=str, help='Name of the hemilineage to process')
    parser.add_argument('--csv', default='hemileage_summary.csv', 
                       help='Path to hemileage summary CSV file (default: hemileage_summary.csv)')
    
    # Processing options
    parser.add_argument('--whole_neuron', action='store_true', 
                       help='Process whole neuron (CBF=False)')
    parser.add_argument('--cbf', action='store_true', 
                       help='Process CBF version (CBF=True)')
    parser.add_argument('--downsampling_factor', type=int, default=10,
                       help='Downsampling factor for mesh processing (default: 10)')
    
    # Other options
    parser.add_argument('--template', default='JRC2018U',
                       help='Target brain template (default: JRC2018U)')
    parser.add_argument('--source', default='FLYWIRE',
                       help='Source coordinate system (default: FLYWIRE)')
    parser.add_argument('--update', action='store_true',
                       help='Force update of existing files')
    
    args = parser.parse_args()
    
    # Validate that at least one processing type is selected
    if not (args.whole_neuron or args.cbf):
        logger.error("Must specify at least one of --whole_neuron or --cbf")
        sys.exit(1)
    
    # Create processor
    processor = HemilineageBatchProcessorV2(args.csv)
    
    # Check if hemilineage exists in the summary
    if args.hemilineage not in processor.df['ito_lee_hemilineage'].values:
        logger.error(f"Hemilineage '{args.hemilineage}' not found in {args.csv}")
        sys.exit(1)
    
    # Process the hemilineage
    results = processor.process_hemilineage(
        hemilineage=args.hemilineage,
        process_whole_neuron=args.whole_neuron,
        process_cbf=args.cbf,
        downsampling_factor=args.downsampling_factor,
        template=args.template,
        source=args.source,
        update=args.update
    )
    
    # Check results
    success = True
    if args.whole_neuron:
        if results['whole_neuron'] is True:
            logger.info(f"Successfully processed whole neuron for {args.hemilineage}")
        else:
            logger.error(f"Failed to process whole neuron for {args.hemilineage}")
            success = False
    
    if args.cbf:
        if results['cbf'] is True:
            logger.info(f"Successfully processed CBF for {args.hemilineage}")
        else:
            logger.error(f"Failed to process CBF for {args.hemilineage}")
            success = False
    
    if success:
        logger.info(f"All requested processing completed successfully for {args.hemilineage}")
        sys.exit(0)
    else:
        logger.error(f"Some processing failed for {args.hemilineage}")
        sys.exit(1)


if __name__ == '__main__':
    main()

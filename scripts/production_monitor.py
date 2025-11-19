#!/usr/bin/env python3
"""
ForgeTrace ML Model Production Monitoring

Tracks prediction confidence distributions, feature drift, and model performance
in production environments. Supports feedback collection for retraining cycles.

Usage:
    python scripts/production_monitor.py --predictions predictions.jsonl --output metrics/

Features:
    - Confidence distribution analysis (flag low-confidence predictions)
    - Class distribution drift detection
    - Feature value drift monitoring (compare to training baselines)
    - Feedback collection workflow (export uncertain predictions for human review)
"""

import argparse
import json
import logging
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
import joblib


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProductionMonitor:
    """Monitor ML model performance in production."""
    
    def __init__(
        self,
        model_path: str = "models/ip_classifier_rf.pkl",
        baseline_stats_path: str = "training_output/dataset/training_dataset.jsonl",
        confidence_threshold: float = 0.70,
    ):
        """
        Initialize production monitor.
        
        Args:
            model_path: Path to trained model pickle
            baseline_stats_path: Path to training dataset for drift detection
            confidence_threshold: Flag predictions below this confidence
        """
        self.model_path = Path(model_path)
        self.baseline_stats_path = Path(baseline_stats_path)
        self.confidence_threshold = confidence_threshold
        
        # Load model
        logger.info(f"Loading model from {self.model_path}")
        self.model = joblib.load(self.model_path)
        
        # Calculate baseline statistics
        self.baseline_stats = self._calculate_baseline_stats()
        
    def _calculate_baseline_stats(self) -> Dict[str, Any]:
        """Calculate feature statistics from training dataset."""
        logger.info("Calculating baseline statistics from training data...")
        
        feature_values = defaultdict(list)
        label_counts = Counter()
        
        with open(self.baseline_stats_path, 'r') as f:
            for line in f:
                example = json.loads(line)
                
                # Track labels
                label_counts[example['label']] += 1
                
                # Track feature values
                for feat_name, feat_val in example['features'].items():
                    if isinstance(feat_val, (int, float)):
                        feature_values[feat_name].append(feat_val)
        
        # Calculate statistics
        stats = {
            'label_distribution': dict(label_counts),
            'total_examples': sum(label_counts.values()),
            'feature_stats': {}
        }
        
        for feat_name, values in feature_values.items():
            stats['feature_stats'][feat_name] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'p25': float(np.percentile(values, 25)),
                'p50': float(np.percentile(values, 50)),
                'p75': float(np.percentile(values, 75)),
                'zero_pct': float(100 * np.sum(np.array(values) == 0) / len(values))
            }
        
        logger.info(f"✅ Baseline calculated from {stats['total_examples']:,} examples")
        return stats
    
    def analyze_predictions(self, predictions_path: str) -> Dict[str, Any]:
        """
        Analyze production predictions for quality metrics.
        
        Args:
            predictions_path: Path to JSONL file with predictions
                Format: {"file_path": str, "prediction": str, "confidence": float, "features": dict}
        
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing predictions from {predictions_path}")
        
        predictions = []
        with open(predictions_path, 'r') as f:
            for line in f:
                predictions.append(json.loads(line))
        
        # Confidence distribution
        confidences = [p['confidence'] for p in predictions]
        low_confidence = [p for p in predictions if p['confidence'] < self.confidence_threshold]
        
        # Class distribution
        class_counts = Counter(p['prediction'] for p in predictions)
        
        # Feature drift analysis
        feature_drift = self._analyze_feature_drift(predictions)
        
        results = {
            'total_predictions': len(predictions),
            'confidence': {
                'mean': float(np.mean(confidences)),
                'std': float(np.std(confidences)),
                'min': float(np.min(confidences)),
                'p25': float(np.percentile(confidences, 25)),
                'p50': float(np.percentile(confidences, 50)),
                'p75': float(np.percentile(confidences, 75)),
                'max': float(np.max(confidences)),
                'low_confidence_count': len(low_confidence),
                'low_confidence_pct': 100 * len(low_confidence) / len(predictions),
            },
            'class_distribution': dict(class_counts),
            'class_distribution_pct': {
                k: 100 * v / len(predictions) for k, v in class_counts.items()
            },
            'feature_drift': feature_drift,
            'low_confidence_files': [
                {'file': p['file_path'], 'prediction': p['prediction'], 'confidence': p['confidence']}
                for p in low_confidence
            ]
        }
        
        return results
    
    def _analyze_feature_drift(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Compare production feature distributions to training baseline."""
        logger.info("Analyzing feature drift...")
        
        drift_scores = {}
        feature_values = defaultdict(list)
        
        # Collect feature values from predictions
        for pred in predictions:
            for feat_name, feat_val in pred.get('features', {}).items():
                if isinstance(feat_val, (int, float)):
                    feature_values[feat_name].append(feat_val)
        
        # Compare to baseline
        for feat_name, values in feature_values.items():
            if feat_name not in self.baseline_stats['feature_stats']:
                continue
            
            baseline = self.baseline_stats['feature_stats'][feat_name]
            prod_mean = np.mean(values)
            prod_std = np.std(values)
            prod_zero_pct = 100 * np.sum(np.array(values) == 0) / len(values)
            
            # Calculate drift metrics
            mean_drift_pct = 100 * abs(prod_mean - baseline['mean']) / (baseline['mean'] + 1e-8)
            std_drift_pct = 100 * abs(prod_std - baseline['std']) / (baseline['std'] + 1e-8)
            zero_drift_pct = abs(prod_zero_pct - baseline['zero_pct'])
            
            drift_scores[feat_name] = {
                'baseline_mean': baseline['mean'],
                'prod_mean': float(prod_mean),
                'mean_drift_pct': float(mean_drift_pct),
                'baseline_std': baseline['std'],
                'prod_std': float(prod_std),
                'std_drift_pct': float(std_drift_pct),
                'baseline_zero_pct': baseline['zero_pct'],
                'prod_zero_pct': float(prod_zero_pct),
                'zero_drift_pct': float(zero_drift_pct),
            }
        
        # Flag high-drift features
        high_drift = {
            name: score for name, score in drift_scores.items()
            if score['mean_drift_pct'] > 50 or score['zero_drift_pct'] > 20
        }
        
        logger.info(f"⚠️  {len(high_drift)} features show significant drift")
        
        return {
            'all_features': drift_scores,
            'high_drift_features': high_drift
        }
    
    def export_for_retraining(
        self,
        predictions_path: str,
        output_path: str,
        filter_confidence: bool = True
    ) -> None:
        """
        Export uncertain predictions for human labeling and retraining.
        
        Args:
            predictions_path: Path to production predictions JSONL
            output_path: Path to write candidates for retraining
            filter_confidence: Only export predictions below confidence threshold
        """
        logger.info("Exporting candidates for retraining...")
        
        exported = 0
        with open(predictions_path, 'r') as infile, open(output_path, 'w') as outfile:
            for line in infile:
                pred = json.loads(line)
                
                # Filter by confidence
                if filter_confidence and pred['confidence'] >= self.confidence_threshold:
                    continue
                
                # Format for manual labeling
                candidate = {
                    'file_path': pred['file_path'],
                    'predicted_label': pred['prediction'],
                    'confidence': pred['confidence'],
                    'features': pred['features'],
                    'human_label': None,  # To be filled by reviewer
                    'notes': "",  # Optional reviewer notes
                    'exported_at': datetime.now().isoformat()
                }
                
                outfile.write(json.dumps(candidate) + '\n')
                exported += 1
        
        logger.info(f"✅ Exported {exported} candidates to {output_path}")
    
    def plot_monitoring_dashboard(
        self,
        analysis_results: Dict[str, Any],
        output_dir: str
    ) -> None:
        """Generate visualization dashboard for monitoring metrics."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Confidence distribution
        logger.info("Generating confidence distribution plot...")
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        conf = analysis_results['confidence']
        axes[0].bar(['Mean', 'P25', 'P50', 'P75'], 
                    [conf['mean'], conf['p25'], conf['p50'], conf['p75']],
                    color=['#2ecc71', '#3498db', '#9b59b6', '#e74c3c'])
        axes[0].axhline(y=self.confidence_threshold, color='red', linestyle='--', 
                        label=f'Threshold ({self.confidence_threshold})')
        axes[0].set_ylabel('Confidence Score')
        axes[0].set_title('Production Confidence Distribution')
        axes[0].legend()
        axes[0].set_ylim([0, 1])
        
        # Low confidence percentage
        low_conf_pct = conf['low_confidence_pct']
        axes[1].pie([low_conf_pct, 100 - low_conf_pct],
                    labels=[f'Low Confidence\n({low_conf_pct:.1f}%)', 
                           f'High Confidence\n({100-low_conf_pct:.1f}%)'],
                    colors=['#e74c3c', '#2ecc71'],
                    autopct='%1.1f%%',
                    startangle=90)
        axes[1].set_title(f'Confidence Threshold: {self.confidence_threshold}')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'confidence_distribution.png', dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"📊 Saved to {output_dir / 'confidence_distribution.png'}")
        
        # 2. Class distribution comparison
        logger.info("Generating class distribution comparison...")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        baseline_dist = self.baseline_stats['label_distribution']
        baseline_total = sum(baseline_dist.values())
        baseline_pct = {k: 100 * v / baseline_total for k, v in baseline_dist.items()}
        
        prod_pct = analysis_results['class_distribution_pct']
        
        labels = sorted(set(list(baseline_pct.keys()) + list(prod_pct.keys())))
        x = np.arange(len(labels))
        width = 0.35
        
        baseline_values = [baseline_pct.get(l, 0) for l in labels]
        prod_values = [prod_pct.get(l, 0) for l in labels]
        
        ax.bar(x - width/2, baseline_values, width, label='Training Baseline', color='#3498db')
        ax.bar(x + width/2, prod_values, width, label='Production', color='#e67e22')
        
        ax.set_xlabel('Class')
        ax.set_ylabel('Percentage (%)')
        ax.set_title('Class Distribution: Training vs Production')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'class_distribution.png', dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"📊 Saved to {output_dir / 'class_distribution.png'}")
        
        # 3. Top 10 drifted features
        logger.info("Generating feature drift visualization...")
        drift = analysis_results['feature_drift']['all_features']
        top_drift = sorted(drift.items(), key=lambda x: x[1]['mean_drift_pct'], reverse=True)[:10]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        feat_names = [name for name, _ in top_drift]
        drift_pcts = [score['mean_drift_pct'] for _, score in top_drift]
        
        colors = ['#e74c3c' if pct > 50 else '#f39c12' if pct > 20 else '#2ecc71' 
                  for pct in drift_pcts]
        
        ax.barh(feat_names, drift_pcts, color=colors)
        ax.axvline(x=50, color='red', linestyle='--', alpha=0.5, label='High Drift (>50%)')
        ax.axvline(x=20, color='orange', linestyle='--', alpha=0.5, label='Medium Drift (>20%)')
        ax.set_xlabel('Mean Drift (%)')
        ax.set_title('Top 10 Features by Mean Drift (Training vs Production)')
        ax.legend()
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'feature_drift.png', dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"📊 Saved to {output_dir / 'feature_drift.png'}")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor ForgeTrace ML model in production"
    )
    parser.add_argument(
        '--predictions',
        type=str,
        required=True,
        help='Path to production predictions JSONL file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='metrics/',
        help='Output directory for monitoring reports (default: metrics/)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='models/ip_classifier_rf.pkl',
        help='Path to trained model pickle'
    )
    parser.add_argument(
        '--baseline',
        type=str,
        default='training_output/dataset/training_dataset.jsonl',
        help='Path to training dataset for baseline statistics'
    )
    parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=0.70,
        help='Confidence threshold for flagging uncertain predictions (default: 0.70)'
    )
    parser.add_argument(
        '--export-retraining',
        type=str,
        help='Export low-confidence predictions for retraining to this path'
    )
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = ProductionMonitor(
        model_path=args.model,
        baseline_stats_path=args.baseline,
        confidence_threshold=args.confidence_threshold
    )
    
    # Analyze predictions
    logger.info("=" * 80)
    logger.info("PRODUCTION MONITORING ANALYSIS")
    logger.info("=" * 80)
    
    results = monitor.analyze_predictions(args.predictions)
    
    # Save analysis results
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results_path = output_dir / 'monitoring_results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"💾 Saved analysis results to {results_path}")
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total Predictions: {results['total_predictions']:,}")
    logger.info(f"Mean Confidence: {results['confidence']['mean']:.3f}")
    logger.info(f"Low Confidence Count: {results['confidence']['low_confidence_count']:,} "
                f"({results['confidence']['low_confidence_pct']:.1f}%)")
    logger.info(f"\nClass Distribution:")
    for cls, pct in sorted(results['class_distribution_pct'].items()):
        count = results['class_distribution'][cls]
        logger.info(f"  {cls}: {count:,} ({pct:.1f}%)")
    
    high_drift = results['feature_drift']['high_drift_features']
    logger.info(f"\nHigh-Drift Features: {len(high_drift)}")
    for feat_name in sorted(high_drift.keys())[:5]:
        logger.info(f"  {feat_name}: {high_drift[feat_name]['mean_drift_pct']:.1f}% mean drift")
    
    # Generate plots
    monitor.plot_monitoring_dashboard(results, args.output)
    
    # Export for retraining if requested
    if args.export_retraining:
        monitor.export_for_retraining(
            args.predictions,
            args.export_retraining,
            filter_confidence=True
        )
    
    logger.info("\n✅ Monitoring analysis complete!")


if __name__ == '__main__':
    main()

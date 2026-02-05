"""
AgentBridge Intelligence Module
AI-driven decision making and optimization for the bridge system
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import statistics
from enum import Enum

from .config import BridgeConfig
from .logging import get_logger
from .models import ModelManager


class OptimizationStrategy(Enum):
    """Optimization strategies for AI-driven decisions"""
    PERFORMANCE_BASED = "performance_based"
    COST_OPTIMIZED = "cost_optimized"
    LOAD_BALANCED = "load_balanced"
    PREDICTIVE = "predictive"


class PerformancePredictor:
    """Predicts performance of different frameworks for specific tasks"""
    
    def __init__(self):
        self.performance_history = {}  # framework -> task_type -> [performance_metrics]
        self.logger = get_logger()
        
    async def record_performance(self, framework: str, task_type: str, 
                               duration: float, success_rate: float, cost: float):
        """Record performance metrics for a framework-task combination"""
        key = f"{framework}:{task_type}"
        if key not in self.performance_history:
            self.performance_history[key] = []
            
        self.performance_history[key].append({
            'timestamp': datetime.now(),
            'duration': duration,
            'success_rate': success_rate,
            'cost': cost
        })
        
        # Keep only last 100 records to prevent memory issues
        if len(self.performance_history[key]) > 100:
            self.performance_history[key] = self.performance_history[key][-100:]
    
    def predict_performance(self, framework: str, task_type: str) -> Dict[str, float]:
        """Predict performance metrics based on historical data"""
        key = f"{framework}:{task_type}"
        if key not in self.performance_history:
            # Return default values if no history
            return {
                'predicted_duration': 10.0,  # Default 10 seconds
                'predicted_success_rate': 0.8,  # Default 80%
                'predicted_cost': 0.05  # Default $0.05
            }
        
        records = self.performance_history[key]
        durations = [r['duration'] for r in records]
        success_rates = [r['success_rate'] for r in records]
        costs = [r['cost'] for r in records]
        
        return {
            'predicted_duration': statistics.mean(durations),
            'predicted_success_rate': statistics.mean(success_rates),
            'predicted_cost': statistics.mean(costs)
        }


class IntelligentRouter:
    """Intelligent routing based on historical performance and predictions"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.predictor = PerformancePredictor()
        self.logger = get_logger()
        
    async def route_intelligently(self, task_description: str, 
                                available_frameworks: List[str],
                                strategy: OptimizationStrategy = OptimizationStrategy.PERFORMANCE_BASED) -> str:
        """Route task to optimal framework based on intelligence"""
        predictions = {}
        
        for framework in available_frameworks:
            prediction = self.predictor.predict_performance(framework, task_description)
            predictions[framework] = prediction
            
        if strategy == OptimizationStrategy.PERFORMANCE_BASED:
            # Choose framework with best predicted success rate
            best_framework = max(predictions.keys(), 
                              key=lambda f: predictions[f]['predicted_success_rate'])
        elif strategy == OptimizationStrategy.COST_OPTIMIZED:
            # Choose framework with lowest predicted cost
            best_framework = min(predictions.keys(), 
                              key=lambda f: predictions[f]['predicted_cost'])
        elif strategy == OptimizationStrategy.LOAD_BALANCED:
            # Choose framework with lowest current load (simplified)
            best_framework = min(predictions.keys(), 
                              key=lambda f: predictions[f]['predicted_duration'])
        else:  # PREDICTIVE
            # Use weighted score considering all factors
            scores = {}
            for framework in predictions:
                pred = predictions[framework]
                # Higher success rate = higher score, lower cost = higher score
                score = pred['predicted_success_rate'] * 100 - pred['predicted_cost'] * 10
                scores[framework] = score
            
            best_framework = max(scores.keys(), key=lambda f: scores[f])
        
        self.logger.info("IntelligentRouter", f"Routed task '{task_description}' to {best_framework} using {strategy.value} strategy")
        return best_framework


class AdaptiveOptimizer:
    """Adaptive optimization based on system feedback"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.logger = get_logger()
        self.system_metrics = {}  # Track system-wide metrics
        self.optimization_history = []  # Track optimization decisions
        
    async def analyze_system_state(self) -> Dict[str, Any]:
        """Analyze current system state for optimization opportunities"""
        # This would typically integrate with monitoring systems
        # For now, we'll simulate system state analysis
        
        analysis = {
            'current_load': len(self.system_metrics.get('recent_requests', [])),
            'avg_response_time': self.system_metrics.get('avg_response_time', 1.0),
            'error_rate': self.system_metrics.get('error_rate', 0.01),
            'resource_utilization': self.system_metrics.get('resource_utilization', 0.5),
            'recommended_strategy': OptimizationStrategy.PERFORMANCE_BASED
        }
        
        # Adjust strategy based on system state
        if analysis['error_rate'] > 0.05:
            analysis['recommended_strategy'] = OptimizationStrategy.LOAD_BALANCED
        elif analysis['resource_utilization'] > 0.8:
            analysis['recommended_strategy'] = OptimizationStrategy.COST_OPTIMIZED
        elif analysis['avg_response_time'] > 5.0:
            analysis['recommended_strategy'] = OptimizationStrategy.PREDICTIVE
        
        return analysis
    
    async def optimize_for_task(self, task_description: str, 
                              available_frameworks: List[str]) -> Tuple[str, Dict[str, Any]]:
        """Optimize framework selection for a specific task"""
        analysis = await self.analyze_system_state()
        strategy = analysis['recommended_strategy']
        
        # Record optimization decision
        decision = {
            'timestamp': datetime.now(),
            'task_description': task_description,
            'available_frameworks': available_frameworks,
            'strategy_used': strategy.value,  # Make sure to add this to analysis
            'system_state': analysis
        }
        self.optimization_history.append(decision)
        
        # Limit history size
        if len(self.optimization_history) > 1000:
            self.optimization_history = self.optimization_history[-1000:]
        
        # Add strategy_used to analysis dict for downstream usage
        analysis['strategy_used'] = strategy.value
        
        return task_description, analysis


class IntelligenceManager:
    """Main intelligence manager for the bridge"""
    
    def __init__(self, config: BridgeConfig, model_manager: ModelManager):
        self.config = config
        self.model_manager = model_manager
        self.intelligent_router = IntelligentRouter(model_manager)
        self.adaptive_optimizer = AdaptiveOptimizer(config)
        self.logger = get_logger()
        
    async def optimize_task_execution(self, task_description: str, 
                                   available_frameworks: List[str]) -> str:
        """Main method to optimize task execution using intelligence"""
        # Use adaptive optimizer to determine best strategy
        _, analysis = await self.adaptive_optimizer.optimize_for_task(
            task_description, available_frameworks
        )
        
        strategy = OptimizationStrategy(analysis['strategy_used'])
        
        # Use intelligent router with determined strategy
        optimal_framework = await self.intelligent_router.route_intelligently(
            task_description, available_frameworks, strategy
        )
        
        return optimal_framework
    
    async def record_task_outcome(self, framework: str, task_type: str, 
                                duration: float, success: bool, cost: float):
        """Record task outcome for learning"""
        success_rate = 1.0 if success else 0.0
        await self.intelligent_router.predictor.record_performance(
            framework, task_type, duration, success_rate, cost
        )
        
        # Update system metrics
        if 'recent_tasks' not in self.adaptive_optimizer.system_metrics:
            self.adaptive_optimizer.system_metrics['recent_tasks'] = []
        
        self.adaptive_optimizer.system_metrics['recent_tasks'].append({
            'timestamp': datetime.now(),
            'framework': framework,
            'task_type': task_type,
            'duration': duration,
            'success': success,
            'cost': cost
        })
        
        # Keep only recent metrics
        if len(self.adaptive_optimizer.system_metrics['recent_tasks']) > 1000:
            self.adaptive_optimizer.system_metrics['recent_tasks'] = \
                self.adaptive_optimizer.system_metrics['recent_tasks'][-1000:]
# metrics_utils.py

import tensorflow as tf
from tensorflow.keras.callbacks import Callback
import numpy as np
import time
import matplotlib.pyplot as plt

class MetricsHistory(Callback):
    def __init__(self):
        super().__init__()
        self.history = {
            'loss': [],
            'val_loss': [],
            'accuracy': [],
            'val_accuracy': [],
            'mae': [],
            'val_mae': [],
            'best_epoch': 0,
            'best_metrics': {},
            'training_time': 0
        }
        self.best_val_loss = float('inf')
        self.training_start_time = None
    
    def on_train_begin(self, logs=None):
        self.training_start_time = time.time()
    
    def on_train_end(self, logs=None):
        if self.training_start_time is not None:
            self.history['training_time'] = time.time() - self.training_start_time
    
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        for metric in ['loss', 'val_loss', 'accuracy', 'val_accuracy', 'mae', 'val_mae']:
            if metric in logs:
                self.history[metric].append(logs[metric])
        
        # Track best epoch based on validation loss
        if logs.get('val_loss', float('inf')) < self.best_val_loss:
            self.best_val_loss = logs.get('val_loss')
            self.history['best_epoch'] = epoch
            self.history['best_metrics'] = {
                'loss': logs.get('loss'),
                'val_loss': logs.get('val_loss'),
                'accuracy': logs.get('accuracy'),
                'val_accuracy': logs.get('val_accuracy'),
                'mae': logs.get('mae'),
                'val_mae': logs.get('val_mae')
            }

def plot_training_history(history, model_name='Model'):
    """Create plots for loss and MAE metrics over epochs"""
    epochs = range(1, len(history['loss']) + 1)
    
    # Create a figure with two subplots
    plt.figure(figsize=(15, 5))
    
    # Plot Loss
    plt.subplot(1, 2, 1)
    plt.plot(epochs, history['loss'], 'b-', label='Training Loss')
    plt.plot(epochs, history['val_loss'], 'r-', label='Validation Loss')
    plt.axvline(x=history['best_epoch'] + 1, color='g', linestyle='--', label='Best Epoch')
    plt.title(f'{model_name} - Loss over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    # Plot MAE
    plt.subplot(1, 2, 2)
    plt.plot(epochs, history['mae'], 'b-', label='Training MAE')
    plt.plot(epochs, history['val_mae'], 'r-', label='Validation MAE')
    plt.axvline(x=history['best_epoch'] + 1, color='g', linestyle='--', label='Best Epoch')
    plt.title(f'{model_name} - MAE over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('MAE')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def print_best_metrics(history, model_name='Model'):
    """Print the best metrics in a standardized format and plot training history"""
    best_metrics = history['best_metrics']
    best_epoch = history['best_epoch']
    training_time = history.get('training_time', 0)
    
    print(f"\n{model_name} - Best Model Metrics (Epoch {best_epoch + 1}):\n")
    print("Training Metrics:")
    print(f"  Loss:     {best_metrics['loss']:.4f}")
    print(f"  Accuracy: {best_metrics['accuracy']:.4f}")
    print(f"  MAE:      {best_metrics['mae']:.4f}")
    print("\nValidation Metrics:")
    print(f"  Loss:     {best_metrics['val_loss']:.4f}")
    print(f"  Accuracy: {best_metrics['val_accuracy']:.4f}")
    print(f"  MAE:      {best_metrics['val_mae']:.4f}")
    
    # Print training time
    hours = int(training_time // 3600)
    minutes = int((training_time % 3600) // 60)
    seconds = int(training_time % 60)
    print(f"\nTotal Training Time: {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    # Plot training history
    plot_training_history(history, model_name)

def plot_model_comparisons(histories):
    """Create comparison plots for multiple models"""
    plt.figure(figsize=(15, 5))
    
    # Plot Loss Comparison
    plt.subplot(1, 2, 1)
    for model_name, history in histories.items():
        epochs = range(1, len(history['loss']) + 1)
        plt.plot(epochs, history['val_loss'], label=f'{model_name}')
    plt.title('Model Comparison - Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    # Plot MAE Comparison
    plt.subplot(1, 2, 2)
    for model_name, history in histories.items():
        epochs = range(1, len(history['mae']) + 1)
        plt.plot(epochs, history['val_mae'], label=f'{model_name}')
    plt.title('Model Comparison - Validation MAE')
    plt.xlabel('Epoch')
    plt.ylabel('MAE')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
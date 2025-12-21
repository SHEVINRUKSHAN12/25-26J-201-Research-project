import torch
import torch.nn as nn
import torch.nn.functional as F

class InteriorFitnessModel(nn.Module):
    """
    A Neural Network to predict the fitness score of a furniture layout.
    Acts as a surrogate model for the expensive geometric fitness evaluation.
    """
    def __init__(self, input_size, hidden_size=128):
        super(InteriorFitnessModel, self).__init__()
        
        # Input Layer
        # input_size = room_features + furniture_features
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.bn1 = nn.BatchNorm1d(hidden_size)
        
        # Hidden Layers
        self.fc2 = nn.Linear(hidden_size, hidden_size * 2)
        self.bn2 = nn.BatchNorm1d(hidden_size * 2)
        
        self.fc3 = nn.Linear(hidden_size * 2, hidden_size)
        self.bn3 = nn.BatchNorm1d(hidden_size)
        
        self.fc4 = nn.Linear(hidden_size, 64)
        
        # Output Layer
        # Predicts a single continuous value (Fitness Score)
        self.output = nn.Linear(64, 1)
        
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = F.relu(self.bn1(self.fc1(x)))
        x = self.dropout(x)
        
        x = F.relu(self.bn2(self.fc2(x)))
        x = self.dropout(x)
        
        x = F.relu(self.bn3(self.fc3(x)))
        x = self.dropout(x)
        
        x = F.relu(self.fc4(x))
        
        # No activation on output for regression (predicting raw score)
        # However, if fitness is 0-100, we might want to clamp or use sigmoid * 100
        # For now, raw regression is safer.
        return self.output(x)

    def save(self, path):
        torch.save(self.state_dict(), path)

    def load(self, path):
        self.state_dict(torch.load(path))

## HEAVILY UNDER DEVELOPMENT, DOES NOT COMPILE. DONT REFER.

import numpy as np
import sys
import dgl
import torch as th

sys.path.append('..')

np.set_printoptions(threshold=sys.maxsize)

def get_training_data():
    profile_graphs = []
    profile_edge_start_node_ids, profile_edge_end_node_ids = th.tensor([0, 1, 2, 3]), th.tensor([1, 2, 3, 0])
    profile_x_coordinates = th.tensor([5, 10, 10, 5])
    profile_y_coordinates = th.tensor([5, 5, 20, 20])

    for x_i in range(-10,10):
        for y_i in range(-10,10):
            g_profile = dgl.graph((profile_edge_start_node_ids, profile_edge_end_node_ids))
            g_profile.ndata['x'] = th.add(profile_x_coordinates,x_i)
            g_profile.ndata['y'] = th.add(profile_y_coordinates,y_i)
            profile_graphs.append(g_profile)

    midcurve_graphs = []
    midcurve_start_node_ids, midcurve_end_node_ids = th.tensor([0]), th.tensor([1])
    midcurve_x_coordinates = th.tensor([7.5, 7.5])
    midcurve_y_coordinates = th.tensor([5, 20])

    for x_i in range(-10,10):
        for y_i in range(-10,10):
            g_midcurve = dgl.graph((midcurve_start_node_ids, midcurve_end_node_ids))
            g_midcurve.ndata['x'] = th.add(midcurve_x_coordinates,x_i)
            g_midcurve.ndata['y'] = th.add(midcurve_y_coordinates,y_i)
            midcurve_graphs.append(g_midcurve)
    return profile_graphs, midcurve_graphs

from dgl.nn import GraphConv

class gnn_encoderdecoder(dgl.nn.Module):
    def __init__(self,profile_graph,midcurve_graph):
        super().__init__()
        self.encoding_dim = 100
        self.epochs = 200
        self.encoder = GraphConv(profile_graph)
        self.decoder = GraphConv(midcurve_graph)

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

def train(profile_graphs, midcurve_graphs):
    model = gnn_encoderdecoder(profile_graphs,midcurve_graphs)
    criterion = dgl.nn.MSELoss()
    learning_rate = 1e-3
    optimizer = th.optim.Adam(
        model.parameters(),
        lr=learning_rate,
    )

    num_epochs = 20
    # do = nn.Dropout()  # comment out for standard AE
    for epoch in range(num_epochs):
        for pg,mg in zip(profile_graphs, midcurve_graphs):
            # ===================forward=====================
            output = model(pg,mg)  # feed <img> (for std AE) or <img_bad> (for denoising AE)
            loss = criterion(output, img.data)
            # ===================backward====================
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        # ===================log========================
        print(f'epoch [{epoch + 1}/{num_epochs}], loss:{loss.item():.4f}')

if __name__ == "__main__":
    ps,ms = get_training_data()
    print(ps)
    print(ms)


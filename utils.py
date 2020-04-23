import numpy as np
import math


def rotate(pc, theta, axis='z'):
    """
    rotate the model clockwise
    :param pc: point cloud, (n, 3)
    :param theta: rotate angle
    :return: new_pc, rotate_matrix
    """
    pc = np.concatenate((pc, np.ones(pc.shape[0]).reshape(pc.shape[0], 1)), axis=1)
    center = np.mean(pc, axis=0)
    rotate_matrix = np.eye(4)
    rotate_matrix[:3, 3] = -center[:3]
    cos = math.cos(theta * math.pi / 180)
    sin = math.sin(theta * math.pi / 180)
    if axis == 'z':
        rotate_matrix[0, :2] = [cos, sin]
        rotate_matrix[1, :2] = [-sin, cos]
    elif axis == 'y':
        rotate_matrix[0, [0, 2]] = [cos, sin]
        rotate_matrix[2, [0, 2]] = [-sin, cos]
    new_pc = np.dot(pc, rotate_matrix.T)[:, :3]
    return new_pc, rotate_matrix


def rotate_delta(delta, axis='z'):
    rotate_matrix = np.eye(4)
    cos = math.cos(delta * math.pi / 180)
    sin = math.sin(delta * math.pi / 180)
    if axis == 'z':
        rotate_matrix[0, :2] = [cos, sin]
        rotate_matrix[1, :2] = [-sin, cos]
    elif axis == 'y':
        rotate_matrix[0, [0, 2]] = [cos, sin]
        rotate_matrix[2, [0, 2]] = [-sin, cos]
    return rotate_matrix

def get_bbox(pc):
    x_min = np.min(pc[:, 0])
    y_min = np.min(pc[:, 1])
    z_min = np.min(pc[:, 2])
    x_max = np.max(pc[:, 0])
    y_max = np.max(pc[:, 1])
    z_max = np.max(pc[:, 2])
    return np.array([x_min, y_min, z_min]), np.array([x_max, y_max, z_max])

if __name__ == '__main__':
    pc = np.load("test_anno/scene0000_00/instance_11.npy")
    rt = np.load("result/scene0000_00/instance_11_6d.npy")
    print(rt)
    import pptk
    v = pptk.viewer(pc)
    v.set(lookat=(0, 0, 0))
    pc = np.concatenate((pc, np.ones(pc.shape[0]).reshape(pc.shape[0], 1)), axis=1)
    v = pptk.viewer(np.dot(pc, rt.T)[:, :3])
    v.set(lookat=(0, 0, 0))

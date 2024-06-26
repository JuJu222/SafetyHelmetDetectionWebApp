import argparse

import cv2
import glob
import numpy as np
import os
import torch

from basicsr.archs.rrdbnet_arch import RRDBNet

def inference():
    # configuration
    model_path = 'net_g_latest.pth'
    folder = opt.input
    device = 'cuda'

    device = torch.device(device)

    # set up model
    model = RRDBNet(
        num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32)
    model.load_state_dict(torch.load(model_path)['params'], strict=True)
    model.eval()
    model = model.to(device)

    for idx, path in enumerate(sorted(glob.glob(os.path.join(folder, '*')))):
        imgname = os.path.splitext(os.path.basename(path))[0]
        print(idx, imgname)
        # read image
        img = cv2.imread(path, cv2.IMREAD_COLOR).astype(np.float32) / 255.
        img = torch.from_numpy(np.transpose(img[:, :, [2, 1, 0]],
                                            (2, 0, 1))).float()
        img = img.unsqueeze(0).to(device)
        # inference
        with torch.no_grad():
            output = model(img)
        # save image
        output = output.data.squeeze().float().cpu().clamp_(0, 1).numpy()
        output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
        output = (output * 255.0).round().astype(np.uint8)
        cv2.imwrite(f'{opt.output}/{imgname}.jpg', output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='', help='input')
    parser.add_argument('--output', default='', help='save results to location')
    opt = parser.parse_args()

    with torch.no_grad():
        inference()

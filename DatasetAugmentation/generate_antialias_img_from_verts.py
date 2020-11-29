'''
@Title: generate_antialias_img_from_vertices.py
@Description: Creates Anti-Aliased Images at different resolutions.
	All generated images are square.
@Author: Philippe Wyder (PMW2125)
'''
import time
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
from multiprocessing import Pool

# Global Parameters
#dataset_path = Path('/media/ron/UbuntuData/Temp/SlenderBeamDataFPA2000')
dataset_path = Path('/home/ron/GeneratedData/data/Linear_DS/')
#dataset_path = Path('/media/ron/6438680D3867DD14/datasets/SlenderBeamData/SlenderBeamDataTF2000')
dataset_startidx = 0
dataset_range = 5001
infile_verts = Path('verts.npy')
large_img_res = 2048
small_img_res = [32, 48, 64, 96, 128]
VERT_MAX = 128
def getimg(verts, color, fill):
	if (color == 'grayscale'):
		c1 = (25,25,25)
		c2=(230,230,230)
	else:
		c1 = (0,0,0)
		c2=(255,255,255)
	im = Image.new('RGB', (large_img_res, large_img_res), c2)
	draw = ImageDraw.Draw(im)
	
	# either use .polygon(), if you want to fill the area with a solid colour
	if (fill):
		draw.polygon( verts, outline=c1,fill=c1 )
	else:
		draw.polygon( verts, outline=c1,fill=c2 )

	# Count Nr of pixels made up by cross-section
	nrpx = im.histogram()[c1[0]]

	# or .line() if you want to control the line thickness, or use both methods together!
	#draw.line( tupVerts+[tupVerts[0]], width=2, fill=black )
	return(im, nrpx)

def process_datapoint(idx):
    # load verts
    datapoint_path = dataset_path / str(idx)
    verts = np.load((datapoint_path / 'numbers' / infile_verts))
    # Center Vertices for Image export
    #  & scale vertices to fit large_img_res sized canvas
    cverts = []
    for pt in verts:
        cverts.append(( (pt[0]+round(VERT_MAX/2))*int(large_img_res/VERT_MAX),
                        (pt[1]+round(VERT_MAX/2))*int(large_img_res/VERT_MAX) ))

    large_img, nr_verts = getimg(cverts, color = 'grayscale', fill = True)

    # save image in various sizes
    for res in small_img_res:
        img_name = 'img_agrayscale_' + str(res) + '.jpg'
        cur_img = large_img.resize((res,res), resample=Image.LANCZOS)
        cur_img.save(datapoint_path / 'img' / img_name)
    print(idx, "processed for resolutions: ", small_img_res)

# Generate data in parallel
if __name__ == '__main__':
    if not dataset_path.exists():
        print("dataset_path doesn't exist")
        quit()
    pool = Pool()
    start_time = time.time()
    pool.map(process_datapoint, range(dataset_startidx, dataset_range))
    print("Finished img data generation in %s seconds" %
            (time.time()-start_time))

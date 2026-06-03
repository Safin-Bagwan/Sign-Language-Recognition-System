import cv2, os, random
import numpy as np
from paths import ARTIFACTS_DIR, GESTURES_DIR, ensure_directories

def get_image_size():
	img_files = list(GESTURES_DIR.glob("*/*.jpg"))
	if not img_files:
		return 50, 50
	img = cv2.imread(str(img_files[0]), 0)
	return img.shape

ensure_directories()
gestures = os.listdir(GESTURES_DIR)
gestures.sort(key = int)
begin_index = 0
end_index = 5
image_x, image_y = get_image_size()

if len(gestures)%5 != 0:
	rows = int(len(gestures)/5)+1
else:
	rows = int(len(gestures)/5)

full_img = None
for i in range(rows):
	col_img = None
	for j in range(begin_index, end_index):
		img_path = GESTURES_DIR / str(j) / f"{random.randint(1, 1200)}.jpg"
		img = cv2.imread(str(img_path), 0)
		if np.any(img == None):
			img = np.zeros((image_y, image_x), dtype = np.uint8)
		if np.any(col_img == None):
			col_img = img
		else:
			col_img = np.hstack((col_img, img))

	begin_index += 5
	end_index += 5
	if np.any(full_img == None):
		full_img = col_img
	else:
		full_img = np.vstack((full_img, col_img))


cv2.imshow("gestures", full_img)
cv2.imwrite(str(ARTIFACTS_DIR / "full_img.jpg"), full_img)
cv2.waitKey(0)

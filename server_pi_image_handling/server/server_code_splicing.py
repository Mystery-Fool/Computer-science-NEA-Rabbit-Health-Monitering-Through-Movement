import cv2
import numpy as np
from matplotlib import pyplot as plt
from stitching.images import Images
from stitching.feature_detector import FeatureDetector
from stitching.feature_matcher import FeatureMatcher
from stitching.subsetter import Subsetter
from stitching.camera_estimator import CameraEstimator
from stitching.camera_adjuster import CameraAdjuster
from stitching.camera_wave_corrector import WaveCorrector
from stitching.warper import Warper
from stitching.cropper import Cropper
from stitching.seam_finder import SeamFinder
from stitching.exposure_error_compensator import ExposureErrorCompensator
from stitching.blender import Blender
#made using https://github.com/OpenStitching/stitching_tutorial/blob/master/docs/Stitching%20Tutorial.md
#+ cropping from https://pyimagesearch.com/2018/12/17/image-stitching-with-opencv-and-python/

class stitch():
	def __init__(self):
		self.first_run=True
		self.images=[]
		self.low_imgs=[]
		self.medium_imgs=[]
		self.final_imgs=[]
		self.feastures=[]
		self.matches=[]
		self.camera=[]
		try: #Repeat over till confidence score is high enough to match images
			self.stitch_and_save("Recived_images\\test13L.png","Recived_images\\test13R.png","Recived_images\\test13.png")
			z=1
		except:
			pass

	def stitch_and_save(self,image1path,image2path,name):
		self.prep_images(image1path,image2path)
		if self.first_run==True:
			self.find_and_match_features()
		
		self.subset()
		if self.first_run==True:
			self.camera_function()

		self.putting_together()
		self.save_img(name)

	def prep_images(self,image1path,image2path): #prepares images
		load_images=[image1path,image2path]
		self.images = Images.of(load_images)
		self.low_imgs = list(self.images.resize(Images.Resolution.LOW))
		self.medium_imgs = list(self.images.resize(Images.Resolution.MEDIUM))
		self.final_imgs = list(self.images.resize(Images.Resolution.FINAL))

	def find_and_match_features(self): #only run once to decrease time taken when image stitching
		finder = FeatureDetector(detector='orb',nfeatures=5000000)#sift gives a good result aswell
		matcher = FeatureMatcher()#matcher_type='affine'
		self.features = [finder.detect_features(img) for img in self.medium_imgs]
		self.matches = matcher.match_features(self.features)
		'''print(matcher.get_confidence_matrix(self.matches))
		all_relevant_matches = matcher.draw_matches_matrix(self.medium_imgs, self.features, self.matches, conf_thresh=0.99, #for testing to see matches
                                                   inliers=True, matchColor=(0, 255, 0))
		keypoints_center_img = finder.draw_keypoints(self.medium_imgs[0], self.features[0])
		plot_image(keypoints_center_img, (15,10))
		keypoints_center_img = finder.draw_keypoints(self.medium_imgs[1], self.features[1])
		plot_image(keypoints_center_img, (15,10))
		for idx1, idx2, img in all_relevant_matches:
			print(f"Matches Image {idx1+1} to Image {idx2+1}")
			plot_image(img, (20,10))'''

	def subset(self): #might not be needed change
		if self.first_run==True:
			self.subsetter = Subsetter(confidence_threshold=1.0)
			self.indices = self.subsetter.get_indices_to_keep(self.features, self.matches)

		self.medium_imgs = self.subsetter.subset_list(self.medium_imgs, self.indices)
		self.low_imgs = self.subsetter.subset_list(self.low_imgs, self.indices)
		self.final_imgs = self.subsetter.subset_list(self.final_imgs, self.indices)
		self.features = self.subsetter.subset_list(self.features, self.indices)
		self.matches = self.subsetter.subset_matches(self.matches, self.indices)
		self.images.subset(self.indices)

	def camera_function(self): # constant
		camera_estimator = CameraEstimator()
		camera_adjuster = CameraAdjuster()
		wave_corrector = WaveCorrector()
		self.cameras = camera_estimator.estimate(self.features, self.matches)
		self.cameras = camera_adjuster.adjust(self.features, self.matches, self.cameras)
		self.cameras = wave_corrector.correct(self.cameras)

	def putting_together(self):
		if self.first_run==True:
			self.warper = Warper()
			self.warper.set_scale(self.cameras)
			low_sizes = self.images.get_scaled_img_sizes(Images.Resolution.LOW)
			camera_aspect = self.images.get_ratio(Images.Resolution.MEDIUM, Images.Resolution.LOW)  # since cameras were obtained on medium imgs
			#warping the smaller images
			warped_low_imgs = list(self.warper.warp_images(self.low_imgs, self.cameras, camera_aspect)) #why do we warp low img first check
			warped_low_masks = list(self.warper.create_and_warp_masks(low_sizes, self.cameras, camera_aspect))
			low_corners, low_sizes = self.warper.warp_rois(low_sizes, self.cameras, camera_aspect)
			#warping the final images
			self.camera_aspect = self.images.get_ratio(Images.Resolution.MEDIUM, Images.Resolution.FINAL) #all above constant

		final_sizes = self.images.get_scaled_img_sizes(Images.Resolution.FINAL)
		warped_final_imgs = list(self.warper.warp_images(self.final_imgs, self.cameras, self.camera_aspect))
		warped_final_masks = list(self.warper.create_and_warp_masks(final_sizes, self.cameras, self.camera_aspect))
		final_corners, final_sizes = self.warper.warp_rois(final_sizes, self.cameras, self.camera_aspect)
		if self.first_run==True:
			self.seam_finder = SeamFinder() #seam finding
			seam_masks = self.seam_finder.find(warped_low_imgs, low_corners, warped_low_masks) #above constant
			self.seam_masks = [self.seam_finder.resize(seam_mask, mask) for seam_mask, mask in zip(seam_masks, warped_final_masks)]
			self.compensator = ExposureErrorCompensator() #exposure error correcting
			self.compensator.feed(low_corners, warped_low_imgs, warped_low_masks) #above constant

		compensated_imgs = [self.compensator.apply(idx, corner, img, mask)  for idx, (img, mask, corner) in enumerate(zip(warped_final_imgs, warped_final_masks, final_corners))]
		#blending together
		if self.first_run==True:
			#self.blender = Blender()
			self.blender=Blender(blender_type='no', blend_strength=5) #Removes blending

		self.blender.prepare(final_corners, final_sizes)#above constant
		for img, mask, corner in zip(compensated_imgs, self.seam_masks, final_corners):
			self.blender.feed(img, mask, corner)

		self.panorama, _ = self.blender.blend()
	
	def save_img(self,name):
		#self.panorama=cv2.cvtColor(self.panorama, cv2.COLOR_BGR2RGB)
		cv2.imwrite(name, self.panorama)
		self.first_run=False
		
'''from matplotlib import pyplot as plt #for testing
import cv2 as cv
import numpy as np

def plot_image(img, figsize_in_inches=(5,5)):
    fig, ax = plt.subplots(figsize=figsize_in_inches)
    ax.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
    plt.show()
    
def plot_images(imgs, figsize_in_inches=(5,5)):
    fig, axs = plt.subplots(1, len(imgs), figsize=figsize_in_inches)
    for col, img in enumerate(imgs):
        axs[col].imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
    plt.show()

if __name__=="__main__":
	import time
	def timer_start():
		global start_time
		start_time=time.time()
	def timer_stop():
		global start_time
		end_time=time.time()
		print(end_time-start_time)

	x=stitch()
	z=0
	while z==0:
		try: #Repeat over till confidence score is high enough to match images
			x.stitch_and_save("server/test13L.png","server/test13R.png","server/testing5testwithoutblend3.png")
			z=1
		except:
			pass
	x.stitch_and_save("server/test9L.png","server/test9R.png","server/testing5testwithoutblend4.png") #Based on previous matched image match this one to same criteria'''
import cv2
import imageio
import os

def create_high_quality_video(image_folder, output_path, fps=30, output_resolution=(1280, 720)):
    images = [img for img in os.listdir(image_folder) if img.endswith(".png") or img.endswith(".jpg")]
    # images = sorted(images, key=lambda x: int(x.split('(')[-1].split(')')[0]))
    images.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))


    video_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, output_resolution)

    for image in images:
        image_path = os.path.join(image_folder, image)
        frame = cv2.imread(image_path)

        # Resize the image to the desired resolution
        frame = cv2.resize(frame, output_resolution)

        video_writer.write(frame)
        
    video_writer.release()
    
# =============================================================================
# Tentative de créer une vidéo avec l'évolution du fuselage à gauche et du 
# déplacement et de la masse à droite
# =============================================================================
def create_high_quality_video_2(image_folder, second_image_folder, output_path, fps=30, output_resolution=(1280, 720)):
    images = [img for img in os.listdir(image_folder) if img.endswith(".png") or img.endswith(".jpg")]
    images.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))

    second_images = [img for img in os.listdir(second_image_folder) if img.endswith(".png") or img.endswith(".jpg")]
    second_images.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))

    video_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, output_resolution)

    for i, (image, second_image) in enumerate(zip(images, second_images)):
        image_path = os.path.join(image_folder, image)
        
        frame = cv2.imread(image_path)
        frame = cv2.resize(frame, output_resolution)

        second_image_path = os.path.join(second_image_folder, second_image)
        second_frame = cv2.imread(second_image_path)
        second_frame = cv2.resize(second_frame, output_resolution)

        # Concatenate frames horizontally

        concat_frame = cv2.hconcat([frame, second_frame])
        concat_frame = cv2.resize(concat_frame, output_resolution)

        video_writer.write(concat_frame)

    video_writer.release()
    
    
    
if __name__ == "__main__":
    input_folder = "C:/Users/lbonn/Documents/EMSE/Cours_EMSE/PI/Code/Plis/Projet_industriel/Code/Calculs_proprietees/constr_emp_V3/Fonctions_batch/GA_global_2/generations/graphes/evoImRigi"
    second_image_folder = "C:/Users/lbonn/Documents/EMSE/Cours_EMSE/PI/Code/Plis/Projet_industriel/Code/Calculs_proprietees/constr_emp_V3/Fonctions_batch/GA_global/generations/graphes/evoDepMasse"
    output_video = "C:/Users/lbonn/Documents/EMSE/Cours_EMSE/PI/Code/Plis/Projet_industriel/Code/Calculs_proprietees/constr_emp_V3/Fonctions_batch/GA_global_2/generations/graphes/NIC300_NG5000_NMI300_2.mp4"
    
    # input_folder = "C:/Users/lbonn/Documents/EMSE/Cours_EMSE/PI/Code/Plis/Projet_industriel/Code/Calculs_proprietees/constr_emp_V3/Fonctions_batch/GA_global_2/generations/graphes/evoImRigi"
    # second_image_folder = "C:/Users/lbonn/Documents/EMSE/Cours_EMSE/PI/Code/Plis/Projet_industriel/Code/Calculs_proprietees/constr_emp_V3/Fonctions_batch/GA_global_2/generations/graphes/evoDepMasse"
    # output_video = "C:/Users/lbonn/Documents/EMSE/Cours_EMSE/PI/Code/Plis/Projet_industriel/Code/Calculs_proprietees/constr_emp_V3/Fonctions_batch/GA_global_2/generations/graphes/output_video.mp4"

    frame_rate = 1.5
    resolution = (1920, 1080)

    create_high_quality_video(input_folder, output_video, frame_rate, resolution)
    # create_high_quality_video_2(input_folder, second_image_folder, output_video, frame_rate, resolution)



import boto3
import base64

from src.libraries.logging_file_format import configure_logger
import logging


logger = logging.getLogger(__name__)
configure_logger(logger, level=logging.INFO)

rekognition_client = boto3.client('rekognition')


def analyze_face(b64image: str):
    # logger.info("starting analyze_face")
    # decode the base64 string to bytes for rekognition
    image_bytes = base64.b64decode(b64image)

    # logger.info("making request in analyze_face")
    response = rekognition_client.detect_faces(
        Image={'Bytes': image_bytes},
        Attributes=['ALL']
    )

    # logger.info(f"received response from rekognition face detect request: {response}")   # commented this out to avoid polluting logs

    #  handle case where response['FaceDetails'] details is empty (no faces)
    if not response['FaceDetails']:
        return None
    else:
        parsed_data_output = []
        for face_details in response['FaceDetails']:
            parsed_data = {
                'bounding_box_width': face_details['BoundingBox']['Width'],
                'bounding_box_height': face_details['BoundingBox']['Height'],
                'bounding_box_left': face_details['BoundingBox']['Left'],
                'bounding_box_top': face_details['BoundingBox']['Top'],
                'age_range_low': face_details['AgeRange']['Low'],
                'age_range_high': face_details['AgeRange']['High'],
                'smile_value': face_details['Smile']['Value'],
                'smile_confidence': face_details['Smile']['Confidence'],
                'eyeglasses_value': face_details['Eyeglasses']['Value'],
                'eyeglasses_confidence': face_details['Eyeglasses']['Confidence'],
                'sunglasses_value': face_details['Sunglasses']['Value'],
                'sunglasses_confidence': face_details['Sunglasses']['Confidence'],
                'gender_value': face_details['Gender']['Value'],
                'gender_confidence': face_details['Gender']['Confidence'],
                'beard_value': face_details['Beard']['Value'],
                'beard_confidence': face_details['Beard']['Confidence'],
                'mustache_value': face_details['Mustache']['Value'],
                'mustache_confidence': face_details['Mustache']['Confidence'],
                'eyes_open_value': face_details['EyesOpen']['Value'],
                'eyes_open_confidence': face_details['EyesOpen']['Confidence'],
                'mouth_open_value': face_details['MouthOpen']['Value'],
                'mouth_open_confidence': face_details['MouthOpen']['Confidence'],
                'emotion_happy_confidence': next(
                    e['Confidence'] for e in face_details['Emotions'] if e['Type'] == 'HAPPY'),
                'emotion_angry_confidence': next(
                    e['Confidence'] for e in face_details['Emotions'] if e['Type'] == 'ANGRY'),
                'emotion_disgusted_confidence': next(
                    e['Confidence'] for e in face_details['Emotions'] if e['Type'] == 'DISGUSTED'),
                'emotion_fear_confidence': next(
                    e['Confidence'] for e in face_details['Emotions'] if e['Type'] == 'FEAR'),
                'emotion_calm_confidence': next(
                    e['Confidence'] for e in face_details['Emotions'] if e['Type'] == 'CALM'),
                'emotion_sad_confidence': next(e['Confidence'] for e in face_details['Emotions'] if e['Type'] == 'SAD'),
                'emotion_surprised_confidence': next(
                    e['Confidence'] for e in face_details['Emotions'] if e['Type'] == 'SURPRISED'),
                'emotion_confused_confidence': next(
                    e['Confidence'] for e in face_details['Emotions'] if e['Type'] == 'CONFUSED'),
            }

            for i, landmark in enumerate(face_details['Landmarks']):
                parsed_data[f'landmark_{landmark}_x'] = landmark['X']
                parsed_data[f'landmark_{landmark}_y'] = landmark['Y']

            parsed_data.update({
                'pose_roll': face_details['Pose']['Roll'],
                'pose_yaw': face_details['Pose']['Yaw'],
                'pose_pitch': face_details['Pose']['Pitch'],
                'quality_brightness': face_details['Quality']['Brightness'],
                'quality_sharpness': face_details['Quality']['Sharpness'],
                'confidence': face_details['Confidence'],
                'face_occluded_value': face_details['FaceOccluded']['Value'],
                'face_occluded_confidence': face_details['FaceOccluded']['Confidence'],
                'eye_direction_yaw': face_details['EyeDirection']['Yaw'],
                'eye_direction_pitch': face_details['EyeDirection']['Pitch'],
                'eye_direction_confidence': face_details['EyeDirection']['Confidence']
            })
            parsed_data_output.append(parsed_data)
        return parsed_data_output

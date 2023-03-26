import io
import os
from google.cloud import vision

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "service-account-file.json"

def run_pipeline(path : str):
    labels_payload = detect_labels(path)
    logos_payload = detect_logos(path)
    final_payload = {}
    if labels_payload != []: final_payload["labels"] = labels_payload
    if logos_payload != []: final_payload["logos"] = logos_payload
    return final_payload 


def localize_objects(path):
    """Localize objects in the local image.
    Args:
    path: The path to the local file.
    """
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    objects = client.object_localization(
        image=image).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))
    print()
    

def localize_objects_uri(uri):
    """Localize objects in the image on Google Cloud Storage

    Args:
    uri: The path to the file in Google Cloud Storage (gs://...)
    """
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    image = vision.Image()
    image.source.image_uri = uri

    objects = client.object_localization(
        image=image).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))
    print()


def detect_labels(path):
    """Detects labels in the file. Returns payload of labels"""
    client = vision.ImageAnnotatorClient()

    # [START vision_python_migration_label_detection]
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.label_detection(image=image)
    labels = response.label_annotations
    payload = []
    print('Labels:')

    for label in labels:
        payload.append(label.description)
        print(label)
        print()
        # print(label.description)

    if response.error.message:
        print()
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    print()
    return payload


def detect_labels_uri(uri):
    """Detects labels in the file located in Google Cloud Storage or on the
    Web."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.label_detection(image=image)
    labels = response.label_annotations
    print('Labels:')

    for label in labels:
        print(label.description)

    if response.error.message:
        print()
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    print()


def detect_logos(path):
    """Detects logos in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    # [START vision_python_migration_logo_detection]
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.logo_detection(image=image)
    logos = response.logo_annotations
    payload = []
    print('Logos:')

    for logo in logos:
        payload.append(logo.description)
        print(logo.description)

    if response.error.message:
        print()
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    # [END vision_python_migration_logo_detection]
    print()
    return payload


def detect_logos_uri(uri):
    """Detects logos in the file located in Google Cloud Storage or on the Web.
    """
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.logo_detection(image=image)
    logos = response.logo_annotations
    print('Logos:')

    for logo in logos:
        print(logo.description)

    if response.error.message:
        print()
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    print()
    

def sample_async_batch_annotate_images(
    input_image_uri="gs://cloud-samples-data/vision/label/wakeupcat.jpg",
    output_uri="gs://your-bucket/prefix/",
):
    """Perform async batch image annotation."""
    client = vision.ImageAnnotatorClient()

    source = {"image_uri": input_image_uri}
    image = {"source": source}
    features = [
        {"type_": vision.Feature.Type.LABEL_DETECTION},
        {"type_": vision.Feature.Type.IMAGE_PROPERTIES},
    ]

    # Each requests element corresponds to a single image.  To annotate more
    # images, create a request element for each image and add it to
    # the array of requests
    requests = [{"image": image, "features": features}]
    gcs_destination = {"uri": output_uri}

    # The max number of responses to output in each JSON file
    batch_size = 2
    output_config = {"gcs_destination": gcs_destination,
                     "batch_size": batch_size}

    operation = client.async_batch_annotate_images(requests=requests, output_config=output_config)

    print("Waiting for operation to complete...")
    response = operation.result(90)

    # The output is written to GCS with the provided output_uri as prefix
    gcs_output_uri = response.output_config.gcs_destination.uri
    print("Output written to GCS with prefix: {}".format(gcs_output_uri))


if __name__ == '__main__':
    # GENERAL PIPELINE
    path : str = 'resources/3iphones.jpg'
    localize_objects(path)
    detect_labels(path)
    detect_logos(path)
    # sample_async_batch_annotate_images('gs://vision_api_sandbox_bucket/shoes_1.jpg', 'gs://vision_api_sandbox_bucket/')
from pathlib import Path

import boto3
import geopandas as gpd
import papermill as pm
from tqdm import tqdm
import click


download_ipynb_dir = Path('planet_download_notebooks')
download_ipynb_dir.mkdir(exist_ok=True)


def get_planet_ids_from_db() -> list:
    bucket_name = 'opera-calval-database-dswx'

    s3 = boto3.resource('s3')
    img_table_obj = s3.Object(bucket_name, 'image.geojson')
    image_table_data = img_table_obj.get()['Body']
    df_planet_images = gpd.read_file(image_table_data)

    planet_ids = df_planet_images.image_name.tolist()
    return planet_ids


def get_local_planet_ids() -> list:
    local_chips_dir = Path('local_chips')
    assert(local_chips_dir.exists())
    planet_id_paths = local_chips_dir.glob('*.tif')
    planet_ids = ['_'.join(path.stem.split('_')[:4])
                  for path in planet_id_paths]
    return planet_ids


def download_planet_img(planet_id: str) -> str:
    out_notebook_path = download_ipynb_dir / f'Download_{planet_id}.ipynb'
    pm.execute_notebook('0_Download_Planet_By_ID.ipynb',
                        output_path=out_notebook_path,
                        parameters={'PLANET_SCENE_ID': planet_id}
                        )
    return out_notebook_path


def classify_planet_img(planet_id):

    out_class_dir = Path(f'classification_outputs/{planet_id}_classification')
    out_class_dir.mkdir(exist_ok=True, parents=True)

    out_notebook_path = out_class_dir / f'Classification_{planet_id}.ipynb'

    pm.execute_notebook('1_Classification_Multiscale_Superpixels_with_Peckel.ipynb',
                        output_path=out_notebook_path,
                        parameters={'PLANET_ID': planet_id}
                        )
    return out_class_dir


@click.command()
@click.option('--download_planet_img', default=False, help='Download Planet Imgs Locally')
@click.option('--use_local_chips', default=True, help='Classify local chips or all Ids in DB')
def main(download_planet_img, use_local_chips):
    planet_ids = get_planet_ids_from_db()
    if use_local_chips:
        planet_ids = get_local_planet_ids()

    def generate_validation_dataset(planet_id):
        if download_planet_img:
            download_planet_img(planet_id)
        out_data = classify_planet_img(planet_id)
        return out_data

    _ = list(map(generate_validation_dataset, tqdm(planet_ids, desc='Generating Validation Dataset')))


if __name__ == '__main__':
    main()

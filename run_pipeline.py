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
    table_name = 'image.geojson'
    df_planet_images = gpd.read_file(f's3://{bucket_name}/{table_name}')
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

    out_class_dir = Path(f'classification_outputs_peckel/{planet_id}')
    out_class_dir.mkdir(exist_ok=True, parents=True)

    out_notebook_path = out_class_dir / f'{planet_id}.ipynb'

    pm.execute_notebook('1_Classification_Multiscale_Superpixels_with_Peckel.ipynb',
                        output_path=out_notebook_path,
                        parameters={'PLANET_ID': planet_id}
                        )
    return out_class_dir


def upload_data():
   out_dir = Path(f'upload_data_notebook/')
   out_dir.mkdir(exist_ok=True, parents=True)

   out_notebook_path = out_dir / f'upload_data.ipynb'

   pm.execute_notebook('2_upload_data_to_s3.ipynb',
                       output_path=out_notebook_path,
                       )
   return out_notebook_path


@click.command()
@click.option('--use_local_chips', default=True, help='Classify only local chips or download all onto disk')
def main(use_local_chips):
    planet_ids = get_planet_ids_from_db()
    if use_local_chips:
        planet_ids = get_local_planet_ids()

    def generate_validation_dataset(planet_id):
        if not use_local_chips:
            print(f'downloading planet image {planet_id}')
            download_planet_img(planet_id)
        print(f'generating ML dataset {planet_id}')
        out_data = classify_planet_img(planet_id)
        return out_data

    _ = list(map(generate_validation_dataset, tqdm(planet_ids, desc='Generating Validation Dataset')))

    upload_data()


if __name__ == '__main__':
    main()

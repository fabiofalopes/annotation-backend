"""
Script to create a test dataset in the database.
"""
from app.infrastructure.database import SessionLocal
from app.domains.datasets.models.models import Dataset

def create_dataset():
    db = SessionLocal()
    try:
        dataset = Dataset(
            name='Test Dataset',
            module_id=1,
            dataset_metadata={'description': 'Test dataset for chat disentanglement'},
            created_by=3
        )
        db.add(dataset)
        db.commit()
        print(f'Dataset created with ID: {dataset.id}')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        db.close()

if __name__ == "__main__":
    create_dataset() 
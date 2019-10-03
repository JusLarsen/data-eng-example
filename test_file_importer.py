import pytest
import file_importer

@pytest.fixture()
def input_file_data():
    return ("mammal is an animal, "
            "dog is a mammal, "
            "frog is an animal, \n"
            "tree is a plant, "
            "plant is an organism, "
            "animal is an organism")

def test_prepare_relationships_for_insertion(input_file_data):
    expected_result = {
        'animal': ['mammal', 'frog'],
        'mammal': ['dog'], 'dog': [],
        'frog': [], 'plant': ['tree'],
        'tree': [],
        'organism': ['plant', 'animal']}
    
    result = file_importer.prepare_relationships_for_insertion(input_file_data)
    assert result == expected_result

    
    

from simple_tf_linter.iterate_dict import value_path_pairs


def test_value_path_list():
    input_dict = {
        'l1': {
            'l2': {
                'l3': {
                    'l4': 1
                }
            }
        },
        'll1': [
            {'ll21': {'ll3': {'ll4': 2}}},
            {'ll22': {'ll32': {'ll42': "3"}}}
        ]
    }
    
    expected_output = {
        (1, 'l1/l2/l3/l4'),
        (2, 'll1/0/ll21/ll3/ll4'),
        ("3", 'll1/1/ll22/ll32/ll42')
    }
    
    output = set(value_path_pairs(input_dict))
    assert output == expected_output, f"Expected: {expected_output}, but got: {output}"
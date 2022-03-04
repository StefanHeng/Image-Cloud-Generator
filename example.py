"""
Example image dictionary generated
"""


d = dict(
    imgs=dict(
        Python=dict(
            name='Python',
            type='Language',
            fluency=0.8
        ),
        markdown=dict(
            name='markdown',
            type='Communication',
            fluency=0.8
        ),
        NumPy=dict(
            name='NumPy',
            type='Framework',
            fluency=0.7
        ),
        AdobePhotoshop=dict(
            name='Adobe Photoshop',
            type='Design',
            fluency=0.7
        ),
        LaTeX=dict(
            name='LaTeX, modified',
            type='Communication',
            fluency=0.7
        ),
        PyCharm=dict(
            name='PyCharm',
            type='IDE',
            fluency=0.6
        ),
        HTML=dict(
            name='HTML',
            type='Language',
            fluency=0.5
        ),
        Marko=dict(
            name='Marko, edited',
            type='Language',
            fluency=0.5
        ),
        JavaScript=dict(
            name='JavaScript',
            type='Language',
            fluency=0.5
        ),
        VisualStudioCode=dict(
            name='Visual Studio Code',
            type='IDE',
            fluency=0.5
        ),
        AdobeIllustrator=dict(
            name='Adobe Illustrator',
            type='Design',
            fluency=0.4
        ),
        hugging_face=dict(
            name='Hugging Face, modified',
            type='Framework',
            fluency=0.5
        ),
        PyTorch=dict(
            name='PyTorch, modified',
            type='Framework',
            fluency=0.4
        ),
        scikit_learn=dict(
            name='scikit_learn, modified',
            type='Framework',
            fluency=0.3
        ),
        matplotlib=dict(
            name='matplotlib, modified',
            type='Framework',
            fluency=0.5
        ),
        Plotly=dict(
            name='Plotly, modified',
            type='Framework',
            fluency=0.4
        ),
        Cpp=dict(
            name='Cpp',
            type='Language',
            fluency=0.3
        ),
        nodejs=dict(
            name='nodejs',
            type='Framework',
            fluency=0.3
        ),
        pandas=dict(
            name='pandas, modified',
            type='Framework',
            fluency=0.3
        ),
        Git=dict(
            name='git',
            type='Framework',
            fluency=0.6
        ),
        LINUX=dict(
            name='Linux, modified',
            type='Other',
            fluency=0.3
        ),
        ShellScript=dict(
            name='Bash, modified',
            type='Other',
            fluency=0.3
        ),
        JetBrains=dict(
            name='JetBrains',
            type='IDE',
            fluency=0.3
        ),
        CLion=dict(
            name='CLion',
            type='IDE',
            fluency=0.3
        ),
        DataSpell=dict(
            name='DataSpell, modified',
            type='IDE',
            fluency=0.3
        ),
        MATLAB=dict(
            name='MATLAB, modified',
            type='Language',
            fluency=0.3
        ),
        Android=dict(
            name='Android, modified',
            type='Language',
            fluency=0.2
        ),
        LESS=dict(
            name='LESS, modified',
            type='Language',
            fluency=0.2
        ),
        Jupyter=dict(
            name='Jupyter, modified',
            type='IDE',
            fluency=0.2
        ),
        JAVA=dict(
            name='JAVA',
            type='Language',
            fluency=0.2
        ),
        OCaml=dict(
            name='OCaml, modified',
            type='Language',
            fluency=0.2
        ),
        AdobePremierePro=dict(
            name='Adobe Premiere Pro',
            type='Design',
            fluency=0.2
        ),
        Figma=dict(
            name='Figma',
            type='Design',
            fluency=0.2
        ),
        Postman=dict(
            name='Postman, modified',  # If `type` unspecified, will set to `Other` type
            fluency=0.2
        ),
        XML=dict(
            name='XML, modified',
            type='Design',
            fluency=0.2
        ),
        ruby=dict(
            name='ruby',
            type='Language',
            fluency=0.1
        ),
        ros=dict(
            name='ROS, modified',
            type='Framework',
            fluency=0.1
        )
    ),
    theme=dict(
        Communication=(255, 127, 26),
        Design=(242, 101, 167),
        Framework=(44, 204, 174),
        IDE=(65, 107, 191),
        Language=(0, 205, 255),
        Other=(47, 56, 64)
    )
)


if __name__ == '__main__':
    import json

    from icecream import ic

    from util import *

    fl_nm = 'example.json'
    with open(fl_nm, 'w') as f:
        json.dump(d, f, indent=4)

    ic(d)
    imgs = d['imgs']
    v = imgs.values()
    types = set(map(lambda x: x['type'] if 'type' in x else 'Other', v))
    ic(types)
    print(f'Image dictionary with {logi(len(v))} images of {logi(len(types))} created')

from setuptools import setup

setup(name = 'qurt',
    url = 'https://github.com/paulgb/qurt',
    author = 'Paul Butler',
    author_email = 'paulgb@gmail.com',
    install_requires = [
        'pygit2==0.20.3',
        'xattr==0.7.5',
    ],
    packages = ['qurt'],
    entry_points = {
        'console_scripts': [
            'qurt = qurt.main:main',
            'git-qurt = qurt.main:main'
        ]
    },
)

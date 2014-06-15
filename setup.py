from setuptools import setup

setup(name = 'crumb',
    url = 'https://github.com/paulgb/crumb',
    author = 'Paul Butler',
    author_email = 'paulgb@gmail.com',
    install_requires = [
        'pygit2==0.20.3',
        'xattr==0.7.5',
    ],
    packages = ['crumb'],
    entry_points = {
        'console_scripts': [
            'crumb = crumb.main:main',
            'git-crumb = crumb.main:main'
        ]
    },
)

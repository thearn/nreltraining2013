#
# This file is autogenerated during plugin quickstart and overwritten during
# plugin makedist. DO NOT CHANGE IT if you plan to use plugin makedist to update 
# the distribution.
#

from setuptools import setup, find_packages

kwargs = {'author': '',
 'author_email': '',
 'classifiers': ['Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering'],
 'description': '',
 'download_url': '',
 'entry_points': '[openmdao.component]\nnrelclass2013.nrelclass2013.BEMPerf=nrelclass2013.nrelclass2013:BEMPerf\nnrelclass2013.nrelclass2013.BEM=nrelclass2013.nrelclass2013:BEM\nnrelclass2013.nrelclass2013.ActuatorDisk=nrelclass2013.nrelclass2013:ActuatorDisk\nnrelclass2013.nrelclass2013.SmallBEM=nrelclass2013.nrelclass2013:SmallBEM\nnrelclass2013.nrelclass2013.BladeElement=nrelclass2013.nrelclass2013:BladeElement\n\n[openmdao.container]\nnrelclass2013.nrelclass2013.BEMPerf=nrelclass2013.nrelclass2013:BEMPerf\nnrelclass2013.nrelclass2013.BEMPerfData=nrelclass2013.nrelclass2013:BEMPerfData\nnrelclass2013.nrelclass2013.BEM=nrelclass2013.nrelclass2013:BEM\nnrelclass2013.nrelclass2013.ActuatorDisk=nrelclass2013.nrelclass2013:ActuatorDisk\nnrelclass2013.nrelclass2013.SmallBEM=nrelclass2013.nrelclass2013:SmallBEM\nnrelclass2013.nrelclass2013.BladeElement=nrelclass2013.nrelclass2013:BladeElement',
 'include_package_data': True,
 'install_requires': ['openmdao.main'],
 'keywords': ['openmdao'],
 'license': '',
 'maintainer': '',
 'maintainer_email': '',
 'name': 'nrelclass2013',
 'package_data': {'nrelclass2013': ['sphinx_build/html/.buildinfo',
                                    'sphinx_build/html/basic_optimization.html',
                                    'sphinx_build/html/bem.html',
                                    'sphinx_build/html/building_component.html',
                                    'sphinx_build/html/genindex.html',
                                    'sphinx_build/html/index.html',
                                    'sphinx_build/html/objects.inv',
                                    'sphinx_build/html/pkgdocs.html',
                                    'sphinx_build/html/py-modindex.html',
                                    'sphinx_build/html/recording_data.html',
                                    'sphinx_build/html/search.html',
                                    'sphinx_build/html/searchindex.js',
                                    'sphinx_build/html/srcdocs.html',
                                    'sphinx_build/html/usage.html',
                                    'sphinx_build/html/_images/add_parameter.png',
                                    'sphinx_build/html/_images/connected_var_comp_editor.png',
                                    'sphinx_build/html/_images/dump_recorder_slot.png',
                                    'sphinx_build/html/_images/empty_project_page.png',
                                    'sphinx_build/html/_images/feedback.png',
                                    'sphinx_build/html/_images/init_project_view.png',
                                    'sphinx_build/html/_images/new_project_modal.png',
                                    'sphinx_build/html/_images/replace_driver.png',
                                    'sphinx_build/html/_modules/index.html',
                                    'sphinx_build/html/_modules/nrelclass2013/nrelclass2013.html',
                                    'sphinx_build/html/_sources/basic_optimization.txt',
                                    'sphinx_build/html/_sources/bem.txt',
                                    'sphinx_build/html/_sources/building_component.txt',
                                    'sphinx_build/html/_sources/index.txt',
                                    'sphinx_build/html/_sources/pkgdocs.txt',
                                    'sphinx_build/html/_sources/recording_data.txt',
                                    'sphinx_build/html/_sources/srcdocs.txt',
                                    'sphinx_build/html/_sources/usage.txt',
                                    'sphinx_build/html/_static/ajax-loader.gif',
                                    'sphinx_build/html/_static/basic.css',
                                    'sphinx_build/html/_static/comment-bright.png',
                                    'sphinx_build/html/_static/comment-close.png',
                                    'sphinx_build/html/_static/comment.png',
                                    'sphinx_build/html/_static/default.css',
                                    'sphinx_build/html/_static/doctools.js',
                                    'sphinx_build/html/_static/down-pressed.png',
                                    'sphinx_build/html/_static/down.png',
                                    'sphinx_build/html/_static/file.png',
                                    'sphinx_build/html/_static/jquery.js',
                                    'sphinx_build/html/_static/minus.png',
                                    'sphinx_build/html/_static/plus.png',
                                    'sphinx_build/html/_static/pygments.css',
                                    'sphinx_build/html/_static/searchtools.js',
                                    'sphinx_build/html/_static/sidebar.js',
                                    'sphinx_build/html/_static/underscore.js',
                                    'sphinx_build/html/_static/up-pressed.png',
                                    'sphinx_build/html/_static/up.png',
                                    'sphinx_build/html/_static/websupport.js',
                                    'test/test_nrelclass2013.py']},
 'package_dir': {'': 'src'},
 'packages': ['nrelclass2013'],
 'url': '',
 'version': '0.1',
 'zip_safe': False}


setup(**kwargs)


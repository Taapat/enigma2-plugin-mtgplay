from distutils.core import setup, Extension
import setup_translate


plugin = 'Extensions.MTGPlay'

setup(name='enigma2-plugin-extensions-mtgplay',
		version='1.0',
		author='Taapat',
		author_email='taapat@gmail.com',
		package_dir={plugin: 'src'},
		packages=[plugin],
		package_data={plugin: ['*.png', 'locale/*/LC_MESSAGES/*.mo']},
		description='Watch MTP play online services',
		cmdclass=setup_translate.cmdclass,
	)

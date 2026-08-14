Python API
==========

Most users only need ``conf.py`` settings and the command line. These modules
are the public surface for extending or embedding the builder — and this page
is itself produced by the builder it documents.

The builder
-----------

.. automodule:: sphinx_vitepress.builder
   :members:

.. automodule:: sphinx_vitepress.translator
   :members: VitepressTranslator, ADMONITIONS, VIRTUAL_PAGES

Escaping and pruning
--------------------

.. automodule:: sphinx_vitepress.escape
   :members:

.. automodule:: sphinx_vitepress.prune
   :members: prune_virtual_page_links

Site generation
---------------

.. automodule:: sphinx_vitepress.sidebar
   :members: build_sidebar, build_nav

.. automodule:: sphinx_vitepress.accents
   :members: resolve, render_css, PRESETS

.. automodule:: sphinx_vitepress.frontmatter
   :members: render

.. automodule:: sphinx_vitepress.inventory
   :members: write_inventory

Deployment
----------

.. automodule:: sphinx_vitepress.versions
   :members:

.. automodule:: sphinx_vitepress.deploy
   :members: run_deploy

.. automodule:: sphinx_vitepress.nodejs
   :members:

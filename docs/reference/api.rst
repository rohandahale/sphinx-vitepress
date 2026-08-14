API
===

Most users only need ``conf.py`` settings and the command line. These modules
are the public surface for extending or embedding the builder. This page is
itself produced by the builder it documents.

Index
-----

.. autosummary::

   sphinx_vitepress.setup
   sphinx_vitepress.builder.VitepressBuilder
   sphinx_vitepress.translator.VitepressTranslator
   sphinx_vitepress.escape.escape_vue
   sphinx_vitepress.prune.prune_virtual_page_links
   sphinx_vitepress.sidebar.build_sidebar
   sphinx_vitepress.sidebar.build_nav
   sphinx_vitepress.accents.resolve
   sphinx_vitepress.accents.render_css
   sphinx_vitepress.frontmatter.render
   sphinx_vitepress.inventory.write_inventory
   sphinx_vitepress.linkcode.make_resolver
   sphinx_vitepress.versions.determine_bases
   sphinx_vitepress.versions.collect_versions
   sphinx_vitepress.deploy.run_deploy
   sphinx_vitepress.nodejs.run_vitepress

The extension
-------------

.. automodule:: sphinx_vitepress
   :members: setup

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

.. automodule:: sphinx_vitepress.linkcode
   :members: make_resolver

Deployment
----------

.. automodule:: sphinx_vitepress.versions
   :members:

.. automodule:: sphinx_vitepress.deploy
   :members: run_deploy

.. automodule:: sphinx_vitepress.nodejs
   :members:

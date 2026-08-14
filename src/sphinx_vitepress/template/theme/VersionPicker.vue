<!-- Version dropdown for versioned deploys.
     Adapted from DocumenterVitepress.jl's VersionPicker.vue (MIT, LuxDL),
     itself adapted from Makie.jl (MIT). See NOTICE.md.

     Reads window.DOC_VERSIONS (from <root>/versions.js) and
     window.DOCS_CURRENT_VERSION (from <base>/siteinfo.js); both scripts are
     injected into <head> by the generated config when a deploy root is set.
     The nav only includes this component on versioned builds. -->

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import VPNavBarMenuGroup from 'vitepress/dist/client/theme-default/components/VPNavBarMenuGroup.vue'
import VPNavScreenMenuGroup from 'vitepress/dist/client/theme-default/components/VPNavScreenMenuGroup.vue'

declare global {
  interface Window {
    DOC_VERSIONS?: string[];
    DOCS_CURRENT_VERSION?: string;
  }
}

declare const __DOCS_DEPLOY_ROOT__: string;

// from vitepress, MIT
function joinPath(base: string, path: string) {
  return `${base}${path}`.replace(/\/+/g, '/')
}

const absoluteRoot = __DOCS_DEPLOY_ROOT__;
const siteOrigin = (typeof window === 'undefined' ? '' : window.location.origin);

function absoluteUrl(relative: string) {
  const withRoot = joinPath(absoluteRoot, relative);
  return siteOrigin + withRoot; // keep the double slash in https:// intact
}

const props = defineProps<{ screenMenu?: boolean }>();
const versions = ref<Array<{ text: string, link: string }>>([]);
const currentVersion = ref('Versions');
const isClient = ref(false);

const isLocalBuild = () => {
  return typeof window !== 'undefined'
    && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
};

const waitForScriptsToLoad = () => {
  return new Promise<boolean>((resolve) => {
    if (isLocalBuild() || typeof window === 'undefined') {
      resolve(false);
      return;
    }
    const checkInterval = setInterval(() => {
      if (window.DOC_VERSIONS && window.DOCS_CURRENT_VERSION) {
        clearInterval(checkInterval);
        resolve(true);
      }
    }, 100);
    setTimeout(() => {
      clearInterval(checkInterval);
      resolve(false);
    }, 5000);
  });
};

const loadVersions = async () => {
  if (typeof window === 'undefined') return;

  try {
    if (isLocalBuild()) {
      versions.value = [{ text: 'dev', link: '/' }];
      currentVersion.value = 'dev';
    } else {
      const scriptsLoaded = await waitForScriptsToLoad();

      if (scriptsLoaded && window.DOC_VERSIONS && window.DOCS_CURRENT_VERSION) {
        versions.value = window.DOC_VERSIONS.map(v => ({
          text: v,
          link: absoluteUrl(`/${v}/`),
        }));
        currentVersion.value = window.DOCS_CURRENT_VERSION;
      } else {
        versions.value = [{ text: 'dev', link: absoluteUrl('/dev/') }];
        currentVersion.value = 'dev';
      }
    }
  } catch (error) {
    console.warn('Error loading versions:', error);
    versions.value = [{ text: 'dev', link: absoluteUrl('/dev/') }];
    currentVersion.value = 'dev';
  }
  isClient.value = true;
};

const versionItems = computed(() => {
  return versions.value.map((v) => ({
    text: v.text,
    link: v.link,
  }));
});

onMounted(() => {
  if (typeof window !== 'undefined') {
    currentVersion.value = window.DOCS_CURRENT_VERSION ?? 'Versions';
    loadVersions();
  }
});
</script>

<template>
  <template v-if="isClient">
    <VPNavBarMenuGroup
      v-if="!screenMenu && versions.length > 0"
      :item="{ text: currentVersion, items: versionItems }"
      class="VPVersionPicker"
    />
    <VPNavScreenMenuGroup
      v-else-if="screenMenu && versions.length > 0"
      :text="currentVersion"
      :items="versionItems"
      class="VPVersionPicker"
    />
  </template>
</template>

<style scoped>
.VPVersionPicker :deep(button .text) {
  color: var(--vp-c-text-1) !important;
}
.VPVersionPicker:hover :deep(button .text) {
  color: var(--vp-c-text-2) !important;
}
</style>

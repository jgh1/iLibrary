import { defineConfig } from "vitepress"

// https://vitepress.dev/reference/site-config
export default defineConfig({
    title: "iLibrary",
    description: "A Python package for IBM i user libraries.",
    themeConfig: {
        search: {
            provider: "local"
        },
        // https://vitepress.dev/reference/default-theme-config
        nav: [
            { text: "Home", link: "/" },
            { text: "Getting started", link: "/usage" }
        ],

        sidebar: [
            {
                items: [
                    { text: "Getting started", link: "/usage" },
                    { text: "Installation", link: "/installation" },
                    { text: "API", link: "/api" },
                    { text: "Troubleshooting", link: "/troubleshooting" },
                ]
            }
        ],

        footer: {
            message: `<a href="https://bytelab.studio/imprint" target="_blank">Imprint</a> <a href="https://bytelab.studio/privacy" target="_blank">Privacy Policy</a>`,
            copyright: `Copyright (c) ${new Date().getFullYear()} Andreas Legner`
        },

        socialLinks: [
            { icon: "github", link: "https://github.com/jgh1/iLibrary" }
        ]
    }
});

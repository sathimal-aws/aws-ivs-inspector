const routes = [
  {
    name: "Auth",
    path: "/auth",
    component: () => import("src/pages/Auth.vue"),
  },

  {
    name: "MainLayout",
    path: "/",
    component: () => import("src/layouts/MainLayout.vue"),
    children: [
      {
        name: "Dashboard",
        path: "/account/:account_id/region/:region/dashboard",
        component: () => import("src/pages/Dashboard.vue"),
        meta: { requiresAuth: true },
      },

      {
        name: "Channels",
        path: "/account/:account_id/region/:region/channels",
        component: () => import("src/pages/Channels.vue"),
        meta: { requiresAuth: true },
      },

      {
        name: "Live Channels",
        path: "/account/:account_id/region/:region/live_channels",
        component: () => import("src/pages/LiveChannels.vue"),
        meta: { requiresAuth: true },
      },

      {
        name: "Channel Details",
        path: "/account/:account_id/region/:region/channel/:channel_id",
        component: () => import("src/components/Channels/ChannelDetails.vue"),
        meta: { requiresAuth: true },
      },

      {
        name: "Session Details",
        path: "/account/:account_id/region/:region/channel/:channel_id/session/:session_id",
        component: () => import("src/components/Sessions/SessionDetails.vue"),
        meta: { requiresAuth: true },
      },
    ],
  },

  {
    path: "/:catchAll(.*)*",
    component: () => import("pages/ErrorNotFound.vue"),
  },
];

export default routes;

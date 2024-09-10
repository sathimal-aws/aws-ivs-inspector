const routes = [
  {
    name: "Auth",
    path: "/auth",
    component: () => import("src/pages/UserLogin.vue"),
  },

  // {
  //   path: "/login",
  //   component: () => import("pages/Login.vue")
  // },
  // {
  //   path: "/forgot_password",
  //   component: () => import("pages/ForgotPassword.vue")
  // },
  // {
  //   path: "/reset_password",
  //   component: () => import("pages/ResetPassword.vue")
  // },
  // {
  //   path: "/register",
  //   component: () => import("pages/Register.vue")
  // },

  {
    name: "MainLayout",
    path: "/",
    component: () => import("src/layouts/MainLayout.vue"),
    children: [
      {
        name: "Settings",
        path: "/account/:account_id/settings",
        component: () => import("src/pages/Settings.vue"),
      },

      {
        name: "Dashboard",
        path: "/account/:account_id/region/:region/dashboard",
        component: () => import("src/pages/Dashboard.vue"),
      },

      {
        name: "Channels",
        path: "/account/:account_id/region/:region/channels",
        component: () => import("src/pages/Channels.vue"),
      },

      {
        name: "Live Channels",
        path: "/account/:account_id/region/:region/live_channels",
        component: () => import("src/pages/LiveChannels.vue"),
      },

      {
        name: "Channel Details",
        path: "/account/:account_id/region/:region/channel/:channel_id",
        component: () => import("src/components/Channels/ChannelDetails.vue"),
      },

      {
        name: "Sessions",
        path: "/account/:account_id/region/:region/channel/:channel_id/sessions",
        component: () => import("src/pages/Sessions.vue"),
      },

      {
        name: "Session Details",
        path: "/account/:account_id/region/:region/channel/:channel_id/session/:session_id",
        component: () => import("src/components/Sessions/SessionDetails.vue"),
      },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: "/:catchAll(.*)*",
    component: () => import("pages/ErrorNotFound.vue"),
  },
];

export default routes;

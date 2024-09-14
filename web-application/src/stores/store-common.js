import { defineStore } from "pinia";

const envVars = import.meta.env;

export const useCommonStore = defineStore("CommonStore", {
  state: () => ({
    account_id: envVars.VITE_ACCOUNT_ID,
    regions: envVars.VITE_IVS_REGIONS.split(","),
    thumbStyle: {
      right: "0px",
      borderRadius: "6px",
      backgroundColor: "#ff6f00",
      width: "2px",
      opacity: 1,
    },

    initialPagination: {
      sortBy: "desc",
      descending: false,
      page: 1,
      rowsPerPage: 100,
    },
  }),

  actions: {
    isValidEmailAddress(email) {
      var re =
        /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(String(email).toLowerCase());
    },
  },
});

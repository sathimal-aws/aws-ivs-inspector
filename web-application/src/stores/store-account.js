import { defineStore } from "pinia";
import { api } from "boot/axios";
import { Notify } from "quasar";
import { useAuthStore } from "./store-auth";

const authStore = useAuthStore();
const envVars = import.meta.env;

const config = {
  headers: {
    Authorization: `Bearer ${authStore.accessToken}`,
    "Access-Control-Allow-Origin": "'*'",
    "Access-Control-Allow-Methods": "'GET, POST, PATCH, PUT, DELETE, OPTIONS'",
    "Access-Control-Allow-Headers": "'Origin, Content-Type, X-Auth-Token'",
  },
};

export const useAccountStore = defineStore("AccountStore", {
  state: () => ({
    accountQuotas: {},
    quotasNextToken: {},
    metrics: {},
  }),

  actions: {
    async getMetrics(ivsRegion) {
      const apis = JSON.parse(
        envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
      );

      try {
        console.log("accessToken:", config);
        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/get-metrics`,
          {
            params: {
              regionName: ivsRegion,
            },
            headers: {
              Authorization: `Bearer ${authStore.accessToken}`,
              "Content-Type": "application/json",
              "Access-Control-Allow-Origin": "'*'",
              "Access-Control-Allow-Methods":
                "'GET, POST, PATCH, PUT, DELETE, OPTIONS'",
              "Access-Control-Allow-Headers":
                "'Origin, Content-Type, X-Auth-Token'",
            },
          }
        );

        console.log("response:", response);
        if (response.status == 200) {
          this.metrics[ivsRegion] = response.data;
        }
        return true;
      } catch (error) {
        console.log("getMetrics err:", error);
        Notify.create({
          color: "negative",
          position: "top",
          message: "Getting metrics failed",
          icon: "report_problem",
        });

        return error;
      }
    },

    async getQuotaProvisioned(serviceCode, ivsRegion) {
      const apis = JSON.parse(
        envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
      );

      try {
        // console.log(serviceCode, ivsRegion);
        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/get-quotas`,
          {
            params: {
              serviceCode: serviceCode,
              nextToken: this.quotasNextToken[ivsRegion] || "",
            },
            headers: {
              Authorization: `${authStore.accessToken}`,
            },
          }
        );

        console.log("response:", response);
        if (response.status == 200) {
          this.accountQuotas[ivsRegion] = response.data?.Quotas;
        }
        return true;
      } catch (error) {
        console.log("getQuotaProvisioned err:", error);
        Notify.create({
          color: "negative",
          position: "top",
          message: "Getting quotas failed",
          icon: "report_problem",
        });

        return error;
      }
    },
  },
});

import { defineStore } from "pinia";
import { api } from "boot/axios";
import { Notify } from "quasar";
import { useCommonStore } from "stores/store-common";

const commonStore = useCommonStore();

const envVars = import.meta.env;

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
        // console.log(ivsRegion);
        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/get-metrics`,
          {
            params: {
              regionName: ivsRegion,
            },
            headers: {
              Authorization: `Bearer ${commonStore.access_token}`,
            },
          }
        );

        console.log("response:", response);
        if (response.status == 200) {
          this.metrics[ivsRegion] = response.data;
        }
        return true;
      } catch (error) {
        console.log(error.message);
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
              Authorization: `Bearer ${commonStore.access_token}`,
            },
          }
        );

        console.log("response:", response);
        if (response.status == 200) {
          this.accountQuotas[ivsRegion] = response.data?.Quotas;
        }
        return true;
      } catch (error) {
        console.log(error.message);
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

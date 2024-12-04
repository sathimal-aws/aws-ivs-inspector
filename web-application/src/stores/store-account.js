import { defineStore } from "pinia";
import { api } from "boot/axios";
import { Notify } from "quasar";
import { useAuthStore } from "./store-auth";

const logger = console; // Use console for logging for now
const authStore = useAuthStore();
const envVars = import.meta.env;

export const useAccountStore = defineStore("AccountStore", {
  state: () => ({
    accountQuotas: {},
    quotasNextToken: {},
    metrics: {},
  }),

  actions: {
    async fetchApiData(ivsRegion, endpoint, params = {}) {
      try {
        const apis = JSON.parse(
          envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
        );
        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/${endpoint}`,
          {
            params,
            headers: { Authorization: `Bearer ${authStore.accessToken}` },
          }
        );

        if (response.status === 200) {
          return response.data;
        }
      } catch (error) {
        logger.error(`Error fetching ${endpoint}: ${error.message}`);
        Notify.create({
          color: "negative",
          position: "top",
          message: `Getting ${endpoint} failed`,
          icon: "report_problem",
        });
      }
      return null;
    },

    async getMetrics(ivsRegion) {
      const data = await this.fetchApiData(ivsRegion, "get-metrics", {
        regionName: ivsRegion,
      });
      if (data) {
        this.metrics[ivsRegion] = data;
        return true;
      }
      return false;
    },

    async getQuotaProvisioned(serviceCode, ivsRegion) {
      const data = await this.fetchApiData(ivsRegion, "get-quotas", {
        serviceCode,
        nextToken: this.quotasNextToken[ivsRegion] || "",
      });
      if (data) {
        this.accountQuotas[ivsRegion] = data?.Quotas;
        this.quotasNextToken[ivsRegion] = data?.nextToken;
        return true;
      }
      return false;
    },
  },
});

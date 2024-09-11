import { defineStore } from "pinia";
import { api } from "boot/axios";
import { Notify } from "quasar";
import { useCommonStore } from "stores/store-common";

const commonStore = useCommonStore();

const envVars = import.meta.env;

// const token =
//   "eyJraWQiOiJkbHNtS1hmYUtxd0tiTHZLR3V4Z0pZUXdPVlo0Y2h0dnBzRDR1TnFYeXRnPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJkMTFiMDUxMC0xMDExLTcwNmEtMjI4Zi1jOWJlMTU5ODc4OGYiLCJjb2duaXRvOmdyb3VwcyI6WyJTdHJlYW1lcnMiLCJBZG1pbiJdLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMi5hbWF6b25hd3MuY29tXC91cy1lYXN0LTJfbHBRWFN3YVJzIiwiY29nbml0bzp1c2VybmFtZSI6ImFkbWluIiwiZ2l2ZW5fbmFtZSI6Iml2cyBpbnNwZWN0b3IiLCJvcmlnaW5fanRpIjoiYmI0MmJkMWQtYjRkZC00NDE4LTkwZTQtNDQ0ZjcwNzA1NGZhIiwiY29nbml0bzpyb2xlcyI6WyJhcm46YXdzOmlhbTo6NzQwMDI0MjQ0NjQ3OnJvbGVcL2l2cy1tb25pdG9yXC9pdnMtbW9uaXRvci1jb2duaXRvX3N0YW5kYXJkX2dyb3VwX3Jlc3RyaWN0ZWRfYWNjZXNzIiwiYXJuOmF3czppYW06Ojc0MDAyNDI0NDY0Nzpyb2xlXC9pdnMtbW9uaXRvclwvaXZzLW1vbml0b3ItY29nbml0b19hZG1pbl9ncm91cF9yZXN0cmljdGVkX2FjY2VzcyJdLCJhdWQiOiIyMW1kbnVrZXR0Y2o0MzkwZWVzb2RhMHRpNyIsImV2ZW50X2lkIjoiYmFjYmIwZDQtNmJmNy00NTExLWI0NzctOTRjZjIwZDA0Y2ZlIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3MjYwNTU5OTUsImV4cCI6MTcyNjA1OTU5NSwiaWF0IjoxNzI2MDU1OTk1LCJmYW1pbHlfbmFtZSI6ImF3cyIsImp0aSI6IjA2ZjFkZmYzLWNmN2MtNDllYS1iMTU2LTFmNzM0ZTg0M2RiMCIsImVtYWlsIjoiYWRtaW5AaXZzLWluc3BlY3Rvci5jb20ifQ.htfd7DjjDvxAnHGsMo2PpfLEnPTcLiy-GLOC3iRD1LNVWYnQNvrCxForI_xNGqvDEgGq6kz53cvUb2V_1XHd5bI8_uWA655H2SU4TLODittBuLFNY-MZLUCPW2SR4Y_oKny75C2mAYg9AoOOHpH3Qct0sHS7pK7Qyp_MPTouvll-EDGtcFtq-YfLN2IK5oxxr3DxQlrq-g_RcpP-KKfJringnCyAnHk2_MmmrxCJ22q0xbFUYh_PetU2P7q7nK0_WNhjC86mNPvhcukFO5R0CiyW4LDpk1sBKG-kN3wcjEbkiS-pi8055p_LK5d4C2CO58sBa00HC-YhkvMZrvY8Ng";

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

import { defineStore } from "pinia";
import { api } from "boot/axios";
import { Notify } from "quasar";
import { useCommonStore } from "stores/store-common";

const commonStore = useCommonStore();

const envVars = import.meta.env;

const token =
  "eyJraWQiOiJ1QVRpcFRHVjVsbUdGRWNtajZ2anJcLzRoeUZmQTFzMERaNDdFeXAwZ01Cbz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4MThiODU4MC03MDAxLTcwMzUtM2QzNC1kMmU0OTZjMmFiMGIiLCJjb2duaXRvOmdyb3VwcyI6WyJBZG1pbiJdLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiY29nbml0bzpwcmVmZXJyZWRfcm9sZSI6ImFybjphd3M6aWFtOjo3NDAwMjQyNDQ2NDc6cm9sZVwvaXZzLWluc3BlY3RvclwvaXZzLWluc3BlY3Rvci1jb2duaXRvX2FkbWluX2dyb3VwX3Jlc3RyaWN0ZWRfYWNjZXNzIiwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMi5hbWF6b25hd3MuY29tXC91cy1lYXN0LTJfM0ZuZzRXc093IiwiY29nbml0bzp1c2VybmFtZSI6ImRlbW8iLCJnaXZlbl9uYW1lIjoibXkgbmFtZSIsIm9yaWdpbl9qdGkiOiJkNGJkMjM1Ni0yZGRmLTQxN2EtYWY2OC1mNTA5NGE3MzQ4ZGQiLCJjb2duaXRvOnJvbGVzIjpbImFybjphd3M6aWFtOjo3NDAwMjQyNDQ2NDc6cm9sZVwvaXZzLWluc3BlY3RvclwvaXZzLWluc3BlY3Rvci1jb2duaXRvX2FkbWluX2dyb3VwX3Jlc3RyaWN0ZWRfYWNjZXNzIl0sImF1ZCI6IjU1ZjJpMjAydDlzZTNzZGRqZWRvYWNmdXU2IiwiZXZlbnRfaWQiOiJjZGYyMDIyZC0zN2FmLTQ3YmMtYWFkZC1lMjAxYWY4M2Y1ZTkiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcyNjAwMzk5OSwiZXhwIjoxNzI2MDE1Mjc3LCJpYXQiOjE3MjYwMTE2NzcsImZhbWlseV9uYW1lIjoidGVzdCBmYW1pbHkgbmFtZSIsImp0aSI6IjIwYTVlNGNkLWExN2MtNGIzNi1iZWQxLTFkNDliYWQxZDliZiIsImVtYWlsIjoiZGVtb0BpdnMtaW5zcGVjdG9yLmNvbSJ9.r0rADgQdBt12xS50dOjxI_y_fpJxLAWzlY4A4bPrp-m81d041Rv7HO_1uC8wD864I6-C27qr0GqjJGVC6LqGQnL5VRhszC1ALM6uYVexYx15gfU2iPHdGyB300EmQpziCkzyaMC13lClmKG4L4PlDSamW_5MzUamBpp4I53BKy2CDjbWbXAk41v1aAGfHYCzIqMzJVxFtYtuSQduw5MEFzYY5rdLv9Wpafof1FRxVQuJ_NtBzCB_JqQ4tXlgHy0sQF3My24u9lgkXXG4DEwTqmBXe5-uh3CyJC8xQ24NagvIZhJXBeCQHPD-dNDIP0KCiZVYTvqMzhL45eMpbKXO9Q";

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
        console.log(ivsRegion);
        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/get-metrics`,
          {
            params: {
              regionName: ivsRegion,
            },
            headers: {
              Authorization: `Bearer ${token}`,
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
        console.log(serviceCode, ivsRegion);
        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/get-quotas`,
          {
            params: {
              serviceCode: serviceCode,
              nextToken: this.quotasNextToken[ivsRegion] || "",
            },
            headers: {
              Authorization: `Bearer ${token}`,
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

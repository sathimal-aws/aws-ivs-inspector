import { defineStore } from "pinia";
import { api } from "boot/axios";
import { Notify } from "quasar";
import { useAuthStore } from "./store-auth";

const authStore = useAuthStore();
const envVars = import.meta.env;

export const useChannelStore = defineStore("ChannelStore", {
  state: () => ({
    channels: {},
    channelsNextToken: {},
    sessionsNextToken: {},
  }),
  getters: {
    channelList: (state) => state.channels,
  },
  actions: {
    async getChannels(ivsRegion) {
      try {
        console.log("getting channel list:", ivsRegion);
        const apis = JSON.parse(
          envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
        );
        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/list-channels`,
          {
            params: {
              nextToken: this.channelsNextToken[ivsRegion] || "",
            },
            headers: {
              Authorization: `Bearer ${authStore.accessToken}`,
            },
          }
        );
        console.log("response:", response.data);

        if (response.status == 200) {
          console.log(this.channels);
          response.data?.channels.map((channel) => {
            const channelId = channel.arn.split("/")[1];
            channel["channelId"] = channelId;
            if (!this.channels[ivsRegion]) {
              this.channels[ivsRegion] = {};
            }
            this.channels[ivsRegion][channelId] = { channelConfig: channel };
          });
          this.channelsNextToken[ivsRegion] = response.data?.nextToken;
        }
        return true;
      } catch {
        Notify.create({
          color: "negative",
          position: "top",
          message: "Loading failed",
          icon: "report_problem",
        });
      }
    },

    async getChannel(channelArn, channelId, ivsRegion) {
      console.log(channelArn);

      try {
        const apis = JSON.parse(
          envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
        );

        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/get-channel`,
          {
            params: {
              channelArn: channelArn,
            },
            headers: {
              Authorization: `Bearer ${authStore.accessToken}`,
            },
          }
        );
        console.log("channelDetails", response.data);

        if (response.status == 200) {
          console.log(
            "channelDetails Exists:",
            this.channels[ivsRegion][channelId]
          );
          if (!this.channels[ivsRegion]) {
            this.channels[ivsRegion] = {};
          }
          if (!this.channels[ivsRegion][channelId]) {
            this.channels[ivsRegion][channelId] = {};
          }

          console.log(
            "this.channels[channelId]",
            this.channels[ivsRegion][channelId]
          );
          this.channels[ivsRegion][channelId].channelConfig = Object.assign(
            this.channels[ivsRegion][channelId]?.channelConfig || {},
            response.data?.channel
          );
        }
        return true;
      } catch (error) {
        console.log(error.message);
        Notify.create({
          color: "negative",
          position: "top",
          message: error.message,
          icon: "report_problem",
        });
        return error;
      }
    },

    async listStreamSessions(channelArn, channelId, ivsRegion) {
      console.log("getting stream sessions:", channelArn, channelId, ivsRegion);
      try {
        const apis = JSON.parse(
          envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
        );

        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/list-stream-sessions`,
          {
            params: {
              channelArn: channelArn,
              nextToken: this.sessionsNextToken[ivsRegion]?.[channelId] || "",
            },
            headers: {
              Authorization: `Bearer ${authStore.accessToken}`,
            },
          }
        );
        // console.log("sessions response:", response.data);
        if (response.status == 200) {
          if (!this.channels[ivsRegion]) {
            this.channels[ivsRegion] = {};
          }
          if (!this.channels[ivsRegion][channelId]) {
            this.channels[ivsRegion][channelId] = {};
          }

          this.channels[ivsRegion][channelId].streamSessions = this.channels[
            ivsRegion
          ][channelId]?.streamSessions
            ? this.channels[ivsRegion][channelId]?.streamSessions.concat(
                response.data?.streamSessions
              )
            : response.data?.streamSessions;

          console.log(
            "region specific channel:",
            this.channels[ivsRegion][channelId]
          );

          if (!this.sessionsNextToken[ivsRegion]) {
            this.sessionsNextToken[ivsRegion] = {};
          }
          this.sessionsNextToken[ivsRegion][channelId] =
            response.data?.nextToken;
        }
        return true;
      } catch (error) {
        Notify.create({
          color: "negative",
          position: "top",
          message: error.message,
          icon: "report_problem",
        });
      }
    },
  },
});

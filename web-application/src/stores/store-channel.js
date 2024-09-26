import { defineStore } from "pinia";
import { api } from "boot/axios";
import { Notify } from "quasar";
import { useAuthStore } from "./store-auth";

const authStore = useAuthStore();
const envVars = import.meta.env;
const logger = console; // Use console for logging for now

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

    async getChannels(ivsRegion) {
      const data = await this.fetchApiData(ivsRegion, "list-channels", {
        nextToken: this.channelsNextToken[ivsRegion] || "",
      });
      if (data) {
        data?.channels.forEach((channel) => {
          const channelId = channel.arn.split("/")[1];
          channel.channelId = channelId;

          this.channels[ivsRegion] = this.channels[ivsRegion] || {};
          this.channels[ivsRegion][channelId] = { channelConfig: channel };
        });
        this.channelsNextToken[ivsRegion] = data?.nextToken;
        return true;
      }
      return false;
    },

    async getChannel(channelArn, channelId, ivsRegion) {
      const data = await this.fetchApiData(ivsRegion, "get-channel", {
        channelArn,
      });
      if (data) {
        this.channels[ivsRegion] = this.channels[ivsRegion] || {};
        this.channels[ivsRegion][channelId] =
          this.channels[ivsRegion][channelId] || {};

        this.channels[ivsRegion][channelId].channelConfig = Object.assign(
          this.channels[ivsRegion][channelId]?.channelConfig || {},
          data?.channel
        );

        return true;
      }
      return false;
    },

    async listStreamSessions(channelArn, channelId, ivsRegion) {
      const data = await this.fetchApiData(ivsRegion, "list-stream-sessions", {
        channelArn: channelArn,
        nextToken: this.sessionsNextToken[ivsRegion]?.[channelId] || "",
      });
      if (data) {
        this.channels[ivsRegion] = this.channels[ivsRegion] || {};
        this.channels[ivsRegion][channelId] = {
          ...this.channels[ivsRegion][channelId],
          streamSessions: this.channels[ivsRegion][channelId]?.streamSessions
            ? this.channels[ivsRegion][channelId]?.streamSessions.concat(
                data?.streamSessions
              )
            : data?.streamSessions,
        };

        this.sessionsNextToken[ivsRegion] =
          this.sessionsNextToken[ivsRegion] || {};
        this.sessionsNextToken[ivsRegion][channelId] = data?.nextToken;
        return true;
      }
      return false;
    },
  },
});

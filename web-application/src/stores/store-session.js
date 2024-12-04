import { defineStore } from "pinia";
import { api } from "boot/axios";
import { Notify } from "quasar";
import { useChannelStore } from "stores/store-channel";
import { useAuthStore } from "./store-auth";

const authStore = useAuthStore();
const channelStore = useChannelStore();
const envVars = import.meta.env;
const logger = console; // Use console for logging for now

export const useSessionStore = defineStore("SessionStore", {
  state: () => ({
    liveSessions: {},
    sessions: {},
    sessionMetrics: {},
    quotas: {},
    streamsNextToken: {},
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
        console.log(error.response.data);
        logger.error(`Error fetching ${endpoint}: ${error.message}`);
        Notify.create({
          color: "negative",
          position: "top",
          message: error.response.data.includes("ChannelNotBroadcasting")
            ? "Channel is not live"
            : error.response.data,
          icon: "report_problem",
        });
      }
      return null;
    },

    async listStreams(ivsRegion) {
      const data = await this.fetchApiData(ivsRegion, "list-streams", {
        nextToken: this.streamsNextToken[ivsRegion] || "",
      });
      if (data) {
        data?.streams.forEach((stream) => {
          const channelId = stream.channelArn.split("/")[1];
          stream.channelId = channelId;

          this.liveSessions[ivsRegion] = this.liveSessions[ivsRegion] || {};
          channelStore.channels[ivsRegion] =
            channelStore.channels[ivsRegion] || {};
          channelStore.channels[ivsRegion][channelId] =
            channelStore.channels[ivsRegion][channelId] || {};

          this.liveSessions[ivsRegion][channelId] = stream;
          channelStore.channels[ivsRegion][channelId].channelConfig = stream;
        });

        this.streamsNextToken[ivsRegion] = data?.nextToken;
        return true;
      }
      return false;
    },

    async getSession(streamId, channelArn, ivsRegion) {
      const data = await this.fetchApiData(ivsRegion, "get-session", {
        stream_id: streamId,
        channel_arn: channelArn,
      });
      if (data) {
        this.sessions[ivsRegion] = this.sessions[ivsRegion] || {};
        this.sessions[ivsRegion][streamId] = {
          ...this.sessions[ivsRegion][streamId],
          ...data,
        };
        return true;
      }
      return false;
    },

    async getStream(streamId, channelArn, ivsRegion) {
      const data = await this.fetchApiData(ivsRegion, "get-stream", {
        channelArn,
      });
      if (data) {
        this.sessions[ivsRegion] = this.sessions[ivsRegion] || {};
        this.sessions[ivsRegion][streamId] = {
          ...this.sessions[ivsRegion][streamId],
          stream: { ...data?.stream },
        };
        return true;
      }
      return false;
    },

    async getIngestMetrics(streamId, channelId, ivsRegion) {
      const data = await this.fetchApiData(ivsRegion, "get-ingest-metrics", {
        stream_id: streamId,
        channel_id: channelId,
      });

      if (data && Object.keys(data).length > 0) {
        this.sessionMetrics[ivsRegion] = this.sessionMetrics[ivsRegion] || {};
        this.sessionMetrics[ivsRegion][streamId] = data;
        return true;
      }
      return false;
    },

    async getLiveStreams(ivsRegion) {
      return this.connectToWebsocket(
        ivsRegion,
        "get_live_streams",
        "get-live-streams",
        "liveStreams"
      );
    },

    async getQuotaProvisioned(serviceCode, ivsRegion) {
      const data = await this.fetchApiData(ivsRegion, "get-quotas", {
        serviceCode,
      });
      if (data) {
        this.quotas = data;
        return true;
      }
      return false;
    },

    // websocket API
    async getSessionEvents(streamId, channelArn, ivsRegion) {
      try {
        const apis = JSON.parse(
          envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
        );

        const ws = new WebSocket(
          `wss://${apis.get_session_events}.execute-api.${ivsRegion}.amazonaws.com/ivs`
        );

        ws.onopen = () => {
          ws.send(
            JSON.stringify({
              action: "get-session-events",
              message: { streamId, channelArn },
            })
          );

          ws.onmessage = (event) => {
            const events = JSON.parse(event.data);

            if (!events.ResponseMetadata && Object.keys(events).length > 0) {
              this.sessions[ivsRegion] = this.sessions[ivsRegion] || {};
              this.sessions[ivsRegion][streamId] = {
                ...this.sessions[ivsRegion][streamId],
                events,
                isLive: !Object.values(events).some(
                  (event) => event.name === "Stream End"
                ),
              };
            }
          };
        };

        ws.onclose = () => {
          logger.info(
            `WebSocket connection for session events closed (streamId: ${streamId}, region: ${ivsRegion})`
          );
        };

        return true;
      } catch (error) {
        logger.error(`Error getting session events: ${error.message}`);
      }
      return false;
    },

    // websocket API
    async getLiveStreams(ivsRegion) {
      try {
        const apis = JSON.parse(
          envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
        );
        console.log(apis);
        const ws = new WebSocket(
          `wss://${apis.get_live_streams}.execute-api.${ivsRegion}.amazonaws.com/ivs`
        );
        ws.onopen = () => {
          console.log("open response:", ws);

          ws.onmessage = (stream) => {
            if (stream.data.length) {
              const streamData = JSON.parse(stream.data);
              const streamId = streamData.detail.stream_id;
              const event = streamData.detail.event_name;
              const channelId = streamData.resources[0].split("/")[1];

              console.log("stream.data", this.liveSessions, event);

              if (event == "Session Created") {
                console.log("session created, adding to the local store");
                const sessionState = {
                  channelArn: streamData.resources[0],
                  startTime: streamData.time,
                  streamId: streamId,
                  channelId: channelId,
                  state: "LIVE",
                };

                console.log(sessionState);

                if (!this.liveSessions[ivsRegion]) {
                  this.liveSessions[ivsRegion] = {};
                }

                this.liveSessions[ivsRegion][channelId] = sessionState;

                if (!channelStore.channels[ivsRegion]) {
                  channelStore.channels[ivsRegion] = {};
                }
                if (!channelStore.channels[ivsRegion][channelId]) {
                  channelStore.channels[ivsRegion][channelId] = {};
                }
                channelStore.channels[ivsRegion][channelId].channelConfig =
                  sessionState;

                console.log("live sessions: ", this.liveSessions[ivsRegion]);
              } else if (event == "Session Ended") {
                console.log("session ended, removing from the local store");
                delete this.liveSessions[ivsRegion][channelId];

                console.log("live sessions: ", this.liveSessions[ivsRegion]);
              }
            }
          };
        };
        ws.close = () => {
          console.log("get live stream connection closed");
        };
        return true;
      } catch (error) {
        console.log(error);
      }

      try {
        ws.onclose = () => console.log("why closed?");
      } catch (error) {
        console.log(error);
        console.log("message:", error.Message);
      }
    },
  },

  getters: {
    sessionList: (state) => state.sessions,
  },
});

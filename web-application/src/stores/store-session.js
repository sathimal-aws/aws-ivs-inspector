import { defineStore } from "pinia";
import { api } from "boot/axios";
import { Notify } from "quasar";
import { useChannelStore } from "stores/store-channel";
import { useAuthStore } from "./store-auth";

const authStore = useAuthStore();
const channelStore = useChannelStore();
const envVars = import.meta.env;

export const useSessionStore = defineStore("SessionStore", {
  state: () => ({
    liveSessions: {},
    sessions: {},
    sessionMetrics: {},
    quotas: {},
    streamsNextToken: {},
  }),

  actions: {
    async listStreams(ivsRegion) {
      // console.log("getting live streams", ivsRegion);
      try {
        const apis = JSON.parse(
          envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
        );

        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/list-streams`,
          {
            params: {
              nextToken: this.streamsNextToken[ivsRegion] || "",
            },
            headers: {
              Authorization: `Bearer ${authStore.accessToken}`,
            },
          }
        );
        // console.log("getSessions response:", response);
        if (response.status == 200) {
          response.data?.streams.map((stream) => {
            // console.log(stream);
            const channelId = stream.channelArn.split("/")[1];
            stream["channelId"] = channelId;

            if (!this.liveSessions[ivsRegion]) {
              this.liveSessions[ivsRegion] = {};
            }
            if (!channelStore.channels[ivsRegion]) {
              channelStore.channels[ivsRegion] = {};
            }
            if (!channelStore.channels[ivsRegion][channelId]) {
              channelStore.channels[ivsRegion][channelId] = {};
            }

            console.log("stream: ", stream);

            this.liveSessions[ivsRegion][channelId] = stream;
            channelStore.channels[ivsRegion][channelId].channelConfig = stream;
          });
          this.streamsNextToken[ivsRegion] = response.data?.nextToken;
          return true;
        }
      } catch (error) {
        console.log(error.message);
        Notify.create({
          color: "negative",
          position: "top",
          message: "Getting live streams failed",
          icon: "report_problem",
        });
        return error;
      }
    },

    async getSession(streamId, channelArn, ivsRegion) {
      try {
        // console.log(streamId, channelArn);
        const apis = JSON.parse(
          envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
        );

        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/get-session`,
          {
            params: {
              stream_id: streamId,
              channel_arn: channelArn,
            },
            headers: {
              Authorization: `Bearer ${authStore.accessToken}`,
            },
          }
        );

        console.log("getSession response:", response);
        if (response.status == 200) {
          if (!this.sessions[ivsRegion]) this.sessions[ivsRegion] = {};
          this.sessions[ivsRegion][streamId] = Object.assign(
            {},
            this.sessions[ivsRegion]?.[streamId],
            response.data?.Item
          );
          return true;
        }
      } catch (error) {
        console.log(error.message);
        Notify.create({
          color: "negative",
          position: "top",
          message: "Getting session details failed",
          icon: "report_problem",
        });
        return error;
      }
    },

    async getStream(streamId, channelArn, ivsRegion) {
      try {
        // console.log(channelArn, streamId, ivsRegion);
        const apis = JSON.parse(
          envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
        );

        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/get-stream`,
          {
            params: {
              channelArn: channelArn,
            },
            headers: {
              Authorization: `Bearer ${authStore.accessToken}`,
            },
          }
        );
        console.log("getStream response:", response);
        if (response.status == 200) {
          if (!this.sessions[ivsRegion]) this.sessions[ivsRegion] = {};
          if (!this.sessions[ivsRegion][streamId]) {
            this.sessions[ivsRegion][streamId] = { stream: {} };
          }

          this.sessions[ivsRegion][streamId].stream = Object.assign(
            {},
            this.sessions[ivsRegion][streamId].stream,
            response.data?.stream
          );
        }
      } catch (error) {
        console.log(error.message);
        Notify.create({
          color: "negative",
          position: "top",
          message: "Getting stream details failed",
          icon: "report_problem",
        });
        return error;
      }
    },

    async getIngestMetrics(streamId, channelId, ivsRegion) {
      try {
        // console.log(streamId, channelId);
        const apis = JSON.parse(
          envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
        );

        const response = await api.get(
          `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivs/get-ingest-metrics`,
          {
            params: {
              stream_id: streamId,
              channel_id: channelId,
            },
            headers: {
              Authorization: `Bearer ${authStore.accessToken}`,
            },
          }
        );

        // console.log(response);

        if (response.status == 200) {
          if (!this.sessionMetrics[ivsRegion])
            this.sessionMetrics[ivsRegion] = {};
          this.sessionMetrics[ivsRegion][streamId] = response?.data;
        }
        return true;
      } catch (error) {
        console.log(error.message);
        Notify.create({
          color: "negative",
          position: "top",
          message: "Getting ingest metrics failed",
          icon: "report_problem",
        });
        return error;
      }
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
          const data = {
            action: "get-session-events",
            message: {
              streamId: streamId,
              channelArn: channelArn,
            },
          };
          const payload = JSON.stringify(data);

          ws.send(payload);

          ws.onmessage = (event) => {
            const events = JSON.parse(event.data);
            // console.log("events:", events);
            if (!events.ResponseMetadata && Object.keys(events)) {
              if (!this.sessions[ivsRegion]) {
                this.sessions[ivsRegion] = {};
              }
              if (!this.sessions[ivsRegion][streamId]) {
                this.sessions[ivsRegion][streamId] = {};
              }
              this.sessions[ivsRegion][streamId].events = events;

              if (
                !Object.values(events).filter(
                  (event) => event.name == "Stream End"
                ).length
              ) {
                // console.log("isLive");
                this.sessions[ivsRegion][streamId].isLive = true;
              }
            }
          };
        };
        ws.close = () => {
          console.log("get events connection closed");
        };
        return true;
      } catch (error) {
        console.log(error);
      }

      ws.onclose = () => console.log("closed");
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

    getQuotaProvisioned(serviceCode, ivsRegion) {
      try {
        console.log(serviceCode);
        const apis = JSON.parse(
          envVars[`VITE_API_${ivsRegion}`].replaceAll("\\", "")
        );

        api
          .get(
            `https://${apis.rest}.execute-api.${ivsRegion}.amazonaws.com/ivsQuotaProvisioned`,
            {
              params: {
                serviceCode: serviceCode,
              },
            }
          )
          .then((response) => {
            if (response.data.statusCode == 200) {
              this.quotas = response.data?.body;
            }
          })
          .catch(() => {
            Notify.create({
              color: "negative",
              position: "top",
              message: "Getting session details failed",
              icon: "report_problem",
            });
          });
      } catch (error) {
        console.log(error.message);
        return error;
      }
    },
  },

  getters: {
    sessionList: (state) => state.sessions,
  },
});

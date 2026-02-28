import { useEffect, useRef, useState } from "react";

interface UseWebSocketOptions {
  url: string | null;
  onMessage?: (data: any) => void;
}

export function useWebSocket({ url, onMessage }: UseWebSocketOptions) {
  const [status, setStatus] = useState<
    "Disconnected" | "Connecting" | "Connected"
  >("Disconnected");

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const heartbeatIntervalRef = useRef<number | null>(null);
  const lastPongRef = useRef<number>(Date.now());
  const retryCountRef = useRef<number>(0);
  const mountedRef = useRef<boolean>(true);

  // ✅ Backoff config
  const BASE_DELAY = 1000;
  const MAX_DELAY = 30000;
  const MAX_RETRIES = 10;

  useEffect(() => {
    if (!url) return;

    mountedRef.current = true;

    const connect = () => {
      if (!mountedRef.current) return;

      // ✅ если вкладка скрыта — не подключаемся
      if (document.visibilityState === "hidden") {
        scheduleReconnect();
        return;
      }

      setStatus("Connecting");

      const ws = new WebSocket(url);
      socketRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) return;

        setStatus("Connected");

        retryCountRef.current = 0; // ✅ сброс попыток
        lastPongRef.current = Date.now();

        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
        }

        heartbeatIntervalRef.current = window.setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ action: "ping" }));
          }

          if (Date.now() - lastPongRef.current > 10000) {
            ws.close();
          }
        }, 5000);
      };

      ws.onmessage = (event: MessageEvent) => {
        if (!mountedRef.current) return;

        const data = JSON.parse(event.data);

        if (data.event === "pong") {
          lastPongRef.current = Date.now();
          return;
        }

        if (onMessage) {
          onMessage(data);
        }
      };

      ws.onclose = (event: CloseEvent) => {
        if (!mountedRef.current) return;

        setStatus("Disconnected");

        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
          heartbeatIntervalRef.current = null;
        }

        // ✅ если сервер закрыл соединение с policy violation (например токен невалидный)
        if (event.code === 1008) {
          console.warn("Policy violation. Stop reconnecting.");
          return;
        }

        scheduleReconnect();
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    const scheduleReconnect = () => {
      if (retryCountRef.current >= MAX_RETRIES) {
        console.warn("Max reconnect attempts reached.");
        return;
      }

      // ✅ Full Jitter strategy
      const maxDelay = Math.min(
        BASE_DELAY * 2 ** retryCountRef.current,
        MAX_DELAY
      );

      const delay = Math.random() * maxDelay;

      console.log(
        `Reconnect attempt #${retryCountRef.current + 1} in ${Math.round(
          delay
        )}ms`
      );

      retryCountRef.current++;

      reconnectTimeoutRef.current = window.setTimeout(() => {
        connect();
      }, delay);
    };

    connect();

    // ✅ reconnect если вкладка стала активной
    const handleVisibilityChange = () => {
      if (
        document.visibilityState === "visible" &&
        status === "Disconnected"
      ) {
        connect();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      mountedRef.current = false;

      document.removeEventListener(
        "visibilitychange",
        handleVisibilityChange
      );

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }

      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }

      socketRef.current?.close();
    };
  }, [url]);

  const send = (payload: any) => {
    const ws = socketRef.current;

    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(JSON.stringify(payload));
  };

  return {
    status,
    send,
  };
}
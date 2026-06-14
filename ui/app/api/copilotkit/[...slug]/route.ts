import {
  CopilotRuntime,
  createCopilotRuntimeHandler,
} from "@copilotkit/runtime/v2";
import { AgnoAgent } from "@ag-ui/agno";

const runtime = new CopilotRuntime({
  agents: {
    default: new AgnoAgent({
      url: process.env.AGNO_AGUI_URL ?? "http://localhost:8000/agui",
    }),
  },
});

const handler = createCopilotRuntimeHandler({
  runtime,
  basePath: "/api/copilotkit",
});

export const GET = handler;
export const POST = handler;
export const OPTIONS = handler;

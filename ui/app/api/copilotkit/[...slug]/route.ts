import {
  CopilotRuntime,
  createCopilotRuntimeHandler,
  TranscriptionService,
  type TranscribeFileOptions,
} from "@copilotkit/runtime/v2";
import { AgnoAgent } from "@ag-ui/agno";

/**
 * Voice dictation: the mic button in the chat input appears automatically once
 * the runtime advertises a transcription service. The recorded audio is POSTed
 * to /api/copilotkit/transcribe, we forward it to OpenAI Whisper, and the text
 * is appended to the input. Needs OPENAI_API_KEY in the Next.js server env.
 */
class WhisperTranscriptionService extends TranscriptionService {
  async transcribeFile({ audioFile }: TranscribeFileOptions): Promise<string> {
    const form = new FormData();
    form.append("file", audioFile);
    form.append("model", "whisper-1");

    const res = await fetch("https://api.openai.com/v1/audio/transcriptions", {
      method: "POST",
      headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
      body: form,
    });
    if (!res.ok) {
      throw new Error(`Transcription failed: ${res.status} ${await res.text()}`);
    }
    const data = await res.json();
    return data.text ?? "";
  }
}

const runtime = new CopilotRuntime({
  agents: {
    default: new AgnoAgent({
      url: process.env.AGNO_AGUI_URL ?? "http://localhost:8000/agui",
    }),
  },
  transcriptionService: new WhisperTranscriptionService(),
});

const handler = createCopilotRuntimeHandler({
  runtime,
  basePath: "/api/copilotkit",
});

export const GET = handler;
export const POST = handler;
export const OPTIONS = handler;

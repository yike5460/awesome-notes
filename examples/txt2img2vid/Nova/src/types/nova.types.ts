export type ContentText = {
  text: string;
};

export type ContentImage = {
  image: {
    format: string;
    source: {
      bytes?: string;
      s3Location?: {
        uri: string;
        bucketOwner?: string;
      };
    };
  };
};

export type ContentVideo = {
  video: {
    format: string;
    source: {
      bytes?: string;
      s3Location?: {
        uri: string;
        bucketOwner?: string;
      };
    };
  };
};

export type ContentType = ContentText | ContentImage | ContentVideo;

export type Message = {
  role: 'user' | 'assistant';
  content: ContentType[];
};

export type SystemMessage = {
  text: string;
};

export type InferenceConfig = {
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  topK?: number;
  stopSequences?: string[];
};

export type NovaRequest = {
  schemaVersion: string;
  messages: Message[];
  system?: SystemMessage[];
  inferenceConfig?: InferenceConfig;
  additionalModelRequestFields?: Record<string, any>;
};

export type NovaResponse = {
  output: {
    message: {
      role: string;
      content: ContentType[];
    };
  };
  usage: {
    inputTokens: number;
    outputTokens: number;
    totalTokens: number;
  };
}; 
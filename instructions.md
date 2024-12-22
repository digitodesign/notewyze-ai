## Project Implementation Guide: NoteWise (Student Learning App)

This guide provides comprehensive instructions for implementing the NoteWise student learning app, leveraging the latest features of Expo, Supabase, Google Gemini, and Phosphorus icons.

**I. Project Overview:**

NoteWise is a mobile application designed to enhance student learning by providing features such as lecture recording and transcription, AI-powered quiz generation, research recommendations, and progress tracking.

**II. Technology Stack:**

  * **Frontend:** React Native (Expo), React Native Paper (Material Design 3), `react-native-vector-icons` (Phosphorus Icons), Expo Router (For Navigation), React Query (For Data Fetching and Caching), Zustand (State Management), Typescript.
  * **Backend:** Supabase (PostgreSQL, Authentication, Storage, Edge Functions)
  * **AI:** Google Gemini API (Speech-to-Text, Text Summarization, Quiz Generation, Research Recommendations)
  * **Development Environment:** VS Code (recommended), Node.js (latest LTS), Expo CLI, Vertex AI Workbench (for initial Gemini API experimentation).

**III. Setup and Tooling:**

1.  **Node.js and npm/yarn:** Install the latest LTS version of Node.js.
2.  **Expo CLI:** `npm install -g expo-cli` or `yarn global add expo-cli`
3.  **VS Code:** Install VS Code and recommended extensions (e.g., ESLint, Prettier, TypeScript).
4.  **Supabase CLI:** `npm install -g supabase` or `yarn global add supabase`
5.  **Vertex AI Workbench:** Set up a user-managed notebook instance for Gemini API experimentation (as described in previous responses). or Google AI Studio

6.  **Git:** Initialize a Git repository for version control.

**IV. Project Setup:**

1.  **Create Expo Project:** `expo init NoteWise --template expo-template-blank-typescript`
2.  **Install Dependencies:**

<!-- end list -->

```bash
cd NoteWise
expo install react-native-paper react-native-vector-icons @react-navigation/native @react-navigation/stack expo-linking expo-constants expo-splash-screen expo-status-bar react-native-safe-area-context react-native-screens react-query zustand
#Install types
expo install @types/react-native-vector-icons
```

3.  **Phosphorus Icons:** Follow the instructions provided in the previous response to integrate Phosphorus icons using `react-native-vector-icons`.
4.  **Supabase Project:**
      * Create a Supabase project on supabase.com.
      * Set up your database schema (users, lectures, quizzes, progress, etc.).
      * Obtain your Supabase URL and anon key.
5.  **Supabase Client:**

<!-- end list -->

```bash
npm install @supabase/supabase-js
#or
yarn add @supabase/supabase-js
```

Create a `supabaseClient.ts` file:

```typescript
import { createClient } from '@supabase/supabase-js'
import AsyncStorage from '@react-native-async-storage/async-storage';

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || '';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      storage: AsyncStorage,
    },
});
```

Make sure to add the `SUPABASE_URL` and `SUPABASE_ANON_KEY` to your `.env` file.

**V. Development Plan (Detailed):**

**Sprint 1: Authentication and Basic UI (2 Weeks):**

  * **Authentication (Supabase):**
      * Implement user signup, sign-in, and sign-out using Supabase Auth.
      * Use Supabase's built-in UI components or create custom UI.
      * Store user data in the Supabase database.
      * Documentation: [Supabase Auth](https://www.google.com/url?sa=E&source=gmail&q=https://supabase.com/docs/guides/auth)
  * **Basic UI Structure (React Native Paper, Expo Router):**
      * Set up navigation using Expo Router.
      * Implement basic UI components (buttons, text inputs, etc.) using React Native Paper.
      * Create basic screens (e.g., Home, Record, Quizzes, Profile).
      * Implement a bottom tab bar navigation.

**Sprint 2: Lecture Recording and Transcription (2 Weeks):**

  * **Audio Recording (Expo AV):**
      * Use `expo-av` to record audio.
      * Implement UI for recording controls (start, stop, pause).
      * Documentation: [Expo AV](https://www.google.com/url?sa=E&source=gmail&q=https://docs.expo.dev/versions/latest/sdk/av/)
  * **Gemini API Integration (Speech-to-Text):**
      * **Backend Service:** Create a backend service (e.g., Cloud Function, serverless function, or dedicated server) to handle the interaction with the Gemini API. This is crucial for security.
      * Send the recorded audio to the backend service.
      * Use the Gemini API to transcribe the audio.
      * Return the transcription to the app.
      * Documentation: [Gemini API](https://www.google.com/url?sa=E&source=gmail&q=https://developers.generativeai.google/)
  * **Display Transcription:** Display the transcription in the app.

**Sprint 3: Quiz Generation and Research Recommendations (2 Weeks):**

  * **Gemini API Integration (Summarization & Quiz Generation):**
      * Use the Gemini API to summarize the transcribed text.
      * Implement logic to generate different quiz question types (multiple-choice, true/false, short answer).
      * Return the generated quizzes to the app.
  * **Gemini API Integration (Research Recommendations):**
      * Use Gemini to generate relevant search terms or resources.
      * Display the recommendations in the app.

**Sprint 4: Data Storage and User Progress (2 Weeks):**

  * **Supabase Database Integration:**
      * Store lectures, transcriptions, quizzes, and user progress in the Supabase database.
      * Use Supabase's real-time features if needed (e.g., for collaborative quizzes).
  * **User Progress Tracking:**
      * Implement logic to track user progress (e.g., quiz scores, completion rates).
      * Display progress in the app.

**Sprint 5: UI/UX Refinement and Testing (1 Week):**

  * **UI/UX Polish:**
      * Implement Material Design 3 styling.
      * Integrate Phosphorus icons.
      * Refine the user flow and overall user experience.
  * **Testing:**
      * Thoroughly test on different devices and platforms.
      * Use Expo's testing tools and services.

**VI. Key Implementation Details:**

  * **Backend Service for Gemini API:** This is essential for security. Do not expose your Gemini API keys in your mobile app.
  * **Error Handling:** Implement robust error handling throughout the app.
  * **State Management (Zustand):** Use Zustand for managing application state.
  * **Data Fetching (React Query):** Use React Query for efficient data fetching, caching, and state management of server data.
  * **Typescript:** Use Typescript to improve code maintainability and prevent errors.

**VII. Documentation and Resources:**

  * **Expo Documentation:** [https://docs.expo.dev/](https://www.google.com/url?sa=E&source=gmail&q=https://docs.expo.dev/)
  * **React Navigation:** [https://reactnavigation.org/](https://www.google.com/url?sa=E&source=gmail&q=https://reactnavigation.org/)
  * **React Native Paper:** [https://callstack.github.io/react-native-paper/](https://www.google.com/url?sa=E&source=gmail&q=https://callstack.github.io/react-native-paper/)
  * **React Query:** [https://tanstack.com/query/latest](https://www.google.com/url?sa=E&source=gmail&q=https://tanstack.com/query/latest)
  * **Zustand:** [https://github.com/pmndrs/zustand](https://www.google.com/url?sa=E&source=gmail&q=https://github.com/pmndrs/zustand)
  * **Supabase Documentation:** [https://supabase.com/docs](https://www.google.com/url?sa=E&source=gmail&q=https://supabase.com/docs)
  * **Gemini API Documentation:** [https://developers.generativeai.google/](https://www.google.com/url?sa=E&source=gmail&q=https://developers.generativeai.google/)

**VIII. Keeping Track of Progress:**

  * **Git:** Use Git for version control and commit regularly with descriptive commit messages.
  * **Project Management Tool:** Use a project management tool like Jira, Trello, or Asana to track tasks, bugs, and progress.
  * **Code Reviews:** Conduct regular code reviews to ensure code quality and knowledge sharing.

This comprehensive guide should provide your software engineer with a clear roadmap for implementing NoteWise. Remember to adapt the plan as needed and encourage open communication and collaboration throughout the development process.

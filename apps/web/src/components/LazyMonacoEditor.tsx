import React, { Suspense } from "react";
import { MonacoEditorProps } from "./MonacoEditor";

const MonacoEditor = React.lazy(() => import("./MonacoEditor").then(module => ({ default: module.MonacoEditor })));

// This component is a wrapper that lazy-loads the MonacoEditor.
// This allows the main application to load without this heavy component,
// improving initial page load performance. The user will see a "Loading..."
// fallback while the component is being fetched.
export const LazyMonacoEditor = (props: MonacoEditorProps) => {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <MonacoEditor {...props} />
        </Suspense>
    );
};

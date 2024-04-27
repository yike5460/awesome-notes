type AppProps = {
    message: string;
    count: number;
    disabled: boolean;
    /** array of a type! */
    names: string[];
    /** string literals to specify exact string values, with a union type to join them together */
    status: "waiting" | "success";
    /** an object with known properties (but could have more at runtime) */
    obj: {
      id: string;
      title: string;
    };
    /** array of objects! (common) */
    objArr: {
      id: string;
      title: string;
    }[];
    /** any non-primitive value - can't access any properties (NOT COMMON but useful as placeholder) */
    obj2: object;
    /** an interface with no required properties - (NOT COMMON, except for things like `React.Component<{}, State>`) */
    obj3: {};
    /** a dict object with any number of properties of the same type */
    dict1: {
      [key: string]: MyTypeHere;
    };
    dict2: Record<string, MyTypeHere>; // equivalent to dict1
    /** function that doesn't take or return anything (VERY COMMON) */
    onClick: () => void;
    /** function with named prop (VERY COMMON) */
    onChange: (id: number) => void;
    /** function type syntax that takes an event (VERY COMMON) */
    onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
    /** alternative function type syntax that takes an event (VERY COMMON) */
    onClick(event: React.MouseEvent<HTMLButtonElement>): void;
    /** any function as long as you don't invoke it (not recommended) */
    onSomething: Function;
    /** an optional prop (VERY COMMON!) */
    optional?: OptionalType;
    /** when passing down the state setter function returned by `useState` to a child component. `number` is an example, swap out with whatever the type of your state */
    setState: React.Dispatch<React.SetStateAction<number>>;
  };

export declare interface AppProps {
    children?: React.ReactNode; // best, accepts everything React can render
    childrenElement: React.JSX.Element; // A single React element
    style?: React.CSSProperties; // to pass through style props
    onChange?: React.FormEventHandler<HTMLInputElement>; // form events! the generic parameter is the type of event.target
    //  more info: https://react-typescript-cheatsheet.netlify.app/docs/advanced/patterns_by_usecase/#wrappingmirroring
    props: Props & React.ComponentPropsWithoutRef<"button">; // to impersonate all the props of a button element and explicitly not forwarding its ref
    props2: Props & React.ComponentPropsWithRef<MyButtonWithForwardRef>; // to impersonate all the props of MyButtonForwardedRef and explicitly forwarding its ref
}

// Declaring type of props - see "Typing Component Props" for more examples
type AppProps = {
    message: string;
}; /* use `interface` if exporting so that consumers can extend */
  
// Easiest way to declare a Function Component; return type is inferred.
const App = ({ message }: AppProps) => <div>{message}</div>;

// you can choose annotate the return type so an error is raised if you accidentally return some other type
const App = ({ message }: AppProps): React.JSX.Element => <div>{message}</div>;

// you can also inline the type declaration; eliminates naming the prop types, but looks repetitive
const App = ({ message }: { message: string }) => <div>{message}</div>;

// Alternatively, you can use `React.FunctionComponent` (or `React.FC`), if you prefer.
// With latest React types and TypeScript 5.1. it's mostly a stylistic choice, otherwise discouraged.
const App: React.FunctionComponent<{ message: string }> = ({ message }) => (
    <div>{message}</div>
);
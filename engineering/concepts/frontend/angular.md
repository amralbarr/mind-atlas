# Angular

Angular is Google's full-featured, opinionated TypeScript frontend framework — unlike [React](nextjs-overview.md)'s "just a library" philosophy, Angular ships routing, forms, [HTTP](../networking/http.md) client, [dependency injection](../programming/fundamentals/dependency-injection.md), and a CLI as one cohesive, batteries-included platform, with a structure and conventions closer to a backend framework like [NestJS](../backend/nestjs/nestjs-overview.md) (both are, in fact, heavily decorator- and dependency-injection-driven, and NestJS's own design was explicitly influenced by Angular's).

## Core Concepts

| Term | Meaning |
|---|---|
| **Component** | A class decorated with `@Component`, pairing a template (HTML), styles, and logic — the fundamental UI building block, conceptually similar to a React [component](components.md) but class-based with decorators |
| **Module (`NgModule`)** | A class decorated with `@NgModule` that groups related components/services/directives together — Angular's unit of compilation and dependency scoping (standalone components, introduced in Angular 14+, are reducing the need for these) |
| **Service** | A class decorated with `@Injectable()`, holding logic/state shared across components — injected via constructor, the same [dependency injection](../programming/fundamentals/dependency-injection.md) pattern as NestJS/Spring |
| **Directive** | Adds behavior to an existing DOM element (`*ngIf`, `*ngFor`) or defines a custom one — components are technically directives with a template attached |
| **Pipe** | A template-only transform for displayed data (`{{ price \| currency }}`) — formatting without touching the underlying value |
| **RxJS Observable** | Angular's primary async primitive — used for [HTTP](../networking/http.md) calls, form value changes, and router events; more powerful but steeper-learning-curve than a plain Promise |
| **Angular CLI** | `ng generate component`, `ng build`, `ng serve` — scaffolding and tooling built into the framework itself, not a separate ecosystem choice like Next.js's various bundler options |

## A Minimal Component

```typescript
@Component({
  selector: 'app-user-card',
  template: `
    <div class="card">
      <h3>{{ user.name }}</h3>
      <button (click)="onSelect()">Select</button>
    </div>
  `
})
export class UserCardComponent {
  @Input() user!: User;
  @Output() selected = new EventEmitter<User>();

  onSelect() {
    this.selected.emit(this.user);
  }
}
```

`@Input()` and `@Output()` are Angular's equivalent of React [props](props-vs-state.md) (data flowing down) and callback props (events flowing up) — the same parent-child communication idea, expressed through decorators instead of function parameters.

## Dependency Injection — Angular's Defining Feature

```typescript
@Injectable({ providedIn: 'root' })  // a singleton, app-wide instance
export class UserService {
  constructor(private http: HttpClient) {}  // HttpClient injected automatically

  getUser(id: string) {
    return this.http.get<User>(`/api/users/${id}`);
  }
}

@Component({ selector: 'app-user-page', template: '...' })
export class UserPageComponent {
  constructor(private userService: UserService) {}  // UserService injected automatically
}
```

Angular's [dependency injection](../programming/fundamentals/dependency-injection.md) container resolves and provides every constructor dependency automatically — the exact same pattern [NestJS](../backend/nestjs/nestjs-overview.md) and [Spring Boot](../programming/java/spring-boot.md) use on the backend, applied to the frontend. This is the single biggest conceptual difference from React, which has no built-in [DI](../programming/fundamentals/dependency-injection.md) system at all (state/dependency sharing happens via Context or external libraries like Zustand/Redux instead).

## Angular vs. React vs. Next.js

| | Angular | React | [Next.js](nextjs-overview.md) |
|---|---|---|---|
| **Scope** | Full framework (routing, forms, [HTTP](../networking/http.md), [DI](../programming/fundamentals/dependency-injection.md), CLI included) | A UI library only | A framework built on top of React |
| **Language** | TypeScript-first, built in | JavaScript, TypeScript optional | JavaScript, TypeScript optional |
| **Component style** | Class + decorators | Function + [hooks](hooks.md) | Function + [hooks](hooks.md) |
| **[Dependency injection](../programming/fundamentals/dependency-injection.md)** | Built-in, first-class | None — Context/external libraries | None — same as React |
| **Async primitive** | RxJS Observables | Promises, [hooks](hooks.md) | Promises, [hooks](hooks.md) |
| **Learning curve** | Steeper ([DI](../programming/fundamentals/dependency-injection.md), RxJS, decorators, modules) | Gentler | Gentler, plus [rendering-strategy](rendering-strategies.md) concepts |
| **Common use case** | Large enterprise SPAs, especially alongside a decorator-based backend (NestJS, Spring, .NET) | Any scale, maximum ecosystem flexibility | SEO-sensitive apps needing [SSR/SSG](rendering-strategies.md) |

## Forms — Template-Driven vs. Reactive

Angular has two distinct, non-interchangeable form approaches:

```typescript
// Reactive forms -- form state and validation defined in the component class
form = new FormGroup({
  email: new FormControl('', [Validators.required, Validators.email]),
});
```

```html
<!-- Template-driven forms -- form state and validation defined in the template -->
<input name="email" ngModel required email>
```

**Reactive forms** are the recommended approach for anything beyond a trivial form — validation logic lives in testable TypeScript rather than scattered across template attributes, mirroring how [data validation](../programming/fundamentals/data-validation.md) is handled as a first-class concern on the backend ([Pydantic](../programming/python/pydantic.md), [class-validator](../backend/api/class-validator.md), Bean Validation) rather than left implicit.

## Routing

```typescript
const routes: Routes = [
  { path: 'users/:id', component: UserPageComponent },
  { path: 'users', component: UserListComponent, canActivate: [AuthGuard] },
];
```

`canActivate` guards are Angular's route-level [authorization](../security/authorization/authorization.md) check — conceptually identical to [NestJS Guards](../backend/nestjs/guards.md) on the backend, just gating client-side navigation instead of a server request.

## Common Questions

**Is Angular still relevant given React's popularity?**
> Yes, particularly in large enterprise environments — its opinionated, all-in-one structure and first-class TypeScript/[DI](../programming/fundamentals/dependency-injection.md) support appeal to teams already standardized on a similarly structured backend (Java/Spring, .NET, or NestJS), where consistency of architecture across the stack is valued over React's greater flexibility and larger talent pool.

**Why does Angular use RxJS instead of plain Promises?**
> RxJS Observables support cancellation, retry, and combining/transforming multiple async streams declaratively (e.g. debouncing a search-as-you-type input) — capabilities a Promise, which represents exactly one eventual value, cannot express on its own.

## Related

- [Next.js Overview](nextjs-overview.md) — the comparison point for a React-based alternative
- [Components](components.md) — the equivalent building-block concept in React
- [Props vs. State](props-vs-state.md) — `@Input()`/`@Output()` are Angular's analog to props
- [Hooks](hooks.md) — React's state/lifecycle primitive, contrasted with Angular's class-based lifecycle [hooks](hooks.md)
- [Dependency Injection](../programming/fundamentals/dependency-injection.md) — Angular's defining architectural feature, shared with NestJS and Spring
- [NestJS Overview](../backend/nestjs/nestjs-overview.md) — the backend framework whose design was explicitly influenced by Angular
- [Spring Boot](../programming/java/spring-boot.md) — another decorator/DI-driven framework with the same architectural DNA
- [Guards](../backend/nestjs/guards.md) — the backend equivalent of Angular's route guards
- [Data Validation](../programming/fundamentals/data-validation.md) — the general pattern Angular's reactive forms implement client-side
- [Rendering Strategies](rendering-strategies.md) — Angular Universal provides SSR, conceptually parallel to Next.js's [rendering strategies](rendering-strategies.md)

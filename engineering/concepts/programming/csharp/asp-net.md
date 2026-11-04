# ASP.NET Core

ASP.NET Core is Microsoft's cross-platform (Windows/Linux/macOS) web framework for C#/.NET — the modern successor to the Windows-only ASP.NET Framework, rewritten from the ground up for performance and open-source cross-platform deployment. Like [Spring Boot](../java/spring-boot.md) and [NestJS](../../backend/nestjs/nestjs-overview.md), it's a dependency-injection-first, attribute/decorator-driven framework for structured, enterprise-scale backends — the three form a direct three-way comparison across Java, TypeScript, and C#.

## Core Concepts

| Term | Meaning |
|---|---|
| **`Program.cs`** | The application's entry point and composition root — in modern minimal-hosting style, both [DI](../fundamentals/dependency-injection.md) registration and the request pipeline are configured here in one file |
| **Controller** | A class inheriting `ControllerBase`, decorated with `[ApiController]` — its public methods (actions) handle [HTTP](../../networking/http.md) requests, the C# equivalent of a `@RestController` in Spring or a `@Controller()` in NestJS |
| **[Dependency Injection](../fundamentals/dependency-injection.md)** | Built into the framework itself (`IServiceCollection`) — no external [DI](../fundamentals/dependency-injection.md) library needed, unlike many other ecosystems |
| **[Middleware](../../backend/middleware.md)** | A pipeline of request/response handlers configured in `Program.cs` (`app.UseAuthentication()`, `app.UseRouting()`) — conceptually identical to [Express/NestJS middleware](../../backend/middleware.md), just composed via method chaining instead of `app.use()` calls |
| **Entity Framework Core (EF Core)** | Microsoft's [ORM](../../backend/data/orm.md) — `DbContext` + `DbSet<T>` model the database, LINQ queries replace raw [SQL](../../databases/relational/sql.md) |
| **Model Binding** | Automatic mapping of request data (route values, query string, [JSON](../fundamentals/json.md) body) onto a C# method parameter or class — the ASP.NET equivalent of a [DTO](../../backend/api/dto.md) combined with automatic parsing |
| **Data Annotations** | Attributes like `[Required]`, `[EmailAddress]`, `[Range]` on a model class — ASP.NET's built-in [data validation](../fundamentals/data-validation.md) mechanism, the C# equivalent of [class-validator](../../backend/api/class-validator.md) decorators or [Pydantic](../python/pydantic.md) field constraints |

## A Minimal Controller

```csharp
[ApiController]
[Route("api/users")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;

    // Constructor injection -- ASP.NET's built-in container supplies IUserService
    public UsersController(IUserService userService)
    {
        _userService = userService;
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<User>> GetUser(int id)
    {
        var user = await _userService.FindByIdAsync(id);
        if (user is null) return NotFound();
        return Ok(user);
    }

    [HttpPost]
    public async Task<ActionResult<User>> CreateUser([FromBody] CreateUserRequest request)
    {
        // ModelState is automatically validated against the request's Data Annotations
        // before this method body ever runs, when [ApiController] is present
        var user = await _userService.CreateAsync(request);
        return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
    }
}
```

With `[ApiController]` present, invalid model state (a failed Data Annotation check) automatically short-circuits into a `400 Bad Request` **before the action method runs at all** — the same "reject at the boundary" principle as [NestJS's `ValidationPipe`](../../backend/api/class-validator.md) or [FastAPI's Pydantic validation](../python/fastapi.md).

## Dependency Injection and Service Lifetimes

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddScoped<IUserService, UserService>();   // one instance per HTTP request
builder.Services.AddSingleton<ICacheService, CacheService>(); // one instance for the app's lifetime
builder.Services.AddTransient<IEmailSender, EmailSender>();   // a new instance every time it's injected

var app = builder.Build();
```

ASP.NET Core's [dependency injection](../fundamentals/dependency-injection.md) container is built in and requires explicitly declaring each service's **[lifetime](../fundamentals/provider-scope.md)** — `Scoped` (per-request, the most common choice for anything touching a database connection), `Singleton` (one instance app-wide), or `Transient` (a fresh instance on every injection). [NestJS](../../backend/nestjs/nestjs-overview.md) providers default to [singleton](../design-patterns/singleton.md) scope unless explicitly marked otherwise — the explicit-by-default lifetime declaration is one of the more distinctive aspects of ASP.NET's [DI](../fundamentals/dependency-injection.md) system; see [Provider Scope](../fundamentals/provider-scope.md) for why NestJS's `REQUEST` and ASP.NET's `Scoped` name the identical lifetime differently.

## Entity Framework Core — The ORM Layer

```csharp
public class User
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public List<Order> Orders { get; set; } = new();  // one-to-many relationship
}

public class AppDbContext : DbContext
{
    public DbSet<User> Users { get; set; }
    public DbSet<Order> Orders { get; set; }
}

// Usage -- LINQ queries compile to SQL
var activeUsers = await dbContext.Users
    .Where(u => u.IsActive)
    .Include(u => u.Orders)   // eager-loads the relationship -- omitting this risks an N+1 query
    .ToListAsync();
```

`.Include()` is EF Core's eager-loading mechanism — omitting it when later accessing `user.Orders` in a loop triggers EF Core's lazy-loading (if enabled) or a `NullReferenceException` (if not), both real instances of the same [N+1 query problem](../../backend/data/n-plus-1-problem.md) that affects every major [ORM](../../backend/data/orm.md).

## ASP.NET Core vs. Spring Boot vs. NestJS

| | ASP.NET Core | [Spring Boot](../java/spring-boot.md) | [NestJS](../../backend/nestjs/nestjs-overview.md) |
|---|---|---|---|
| Language | C# | Java / Kotlin | TypeScript |
| [DI](../fundamentals/dependency-injection.md) | Built into the framework | Spring's [IoC](../fundamentals/inversion-of-control.md) container | Built into the framework |
| [ORM](../../backend/data/orm.md) | Entity Framework Core | Spring Data JPA (Hibernate) | TypeORM / Prisma (not built-in) |
| Validation | Data Annotations | Bean Validation | [class-validator](../../backend/api/class-validator.md) |
| Async model | `async`/`await`, Task-based throughout | Blocking by default; WebFlux for reactive | Promise/`async`-`await`-based, Node.js [event loop](../javascript/event-loop.md) |
| Hosting | Cross-platform (Kestrel server) | Cross-platform (embedded Tomcat) | Cross-platform (Node.js) |

## Minimal APIs — The Lightweight Alternative

For a small service that doesn't need the full controller/MVC structure, ASP.NET Core also supports a route-per-lambda style introduced in .NET 6:

```csharp
app.MapGet("/users/{id}", async (int id, IUserService userService) =>
{
    var user = await userService.FindByIdAsync(id);
    return user is not null ? Results.Ok(user) : Results.NotFound();
});
```

This is architecturally closer to [Express](../../networking/http.md) or a bare [FastAPI](../python/fastapi.md) route than to the controller-based MVC style above — useful for microservices where the full controller ceremony isn't warranted.

## Common Questions

**Is ASP.NET Core the same as the old "ASP.NET" / ".NET Framework"?**
> No — ASP.NET Core is a ground-up rewrite, cross-platform and open-source, while the original ASP.NET (now often called ".NET Framework") is Windows-only and in maintenance mode. All new development targets ASP.NET Core on modern .NET (.NET 6/7/8+).

**Why does `[ApiController]` matter specifically?**
> It enables several API-specific conveniences automatically: automatic `400` responses on invalid model state, automatic inference of `[FromBody]`/`[FromRoute]` binding sources, and problem-details-formatted error responses — without it, a controller behaves like a traditional MVC view-rendering controller instead of a pure API one.

## Related

- [Spring Boot](../java/spring-boot.md) — the closest Java equivalent in philosophy and structure
- [NestJS Overview](../../backend/nestjs/nestjs-overview.md) — the closest TypeScript equivalent
- [Dependency Injection](../fundamentals/dependency-injection.md) — built into the framework, with explicit service lifetimes
- [Provider Scope](../fundamentals/provider-scope.md) — the general concept behind `AddSingleton`/`AddScoped`/`AddTransient`, including the NestJS/[Spring Boot](../java/spring-boot.md) equivalents
- [ORM](../../backend/data/orm.md) — Entity Framework Core is ASP.NET's [ORM](../../backend/data/orm.md) layer
- [The N+1 Query Problem](../../backend/data/n-plus-1-problem.md) — the same `.Include()`/eager-loading concern as every other [ORM](../../backend/data/orm.md)
- [Data Validation](../fundamentals/data-validation.md) — Data Annotations implement the general pattern
- [DTO](../../backend/api/dto.md) — ASP.NET's model-binding target classes serve the same role
- [Middleware](../../backend/middleware.md) — the request pipeline concept, shared with Express/NestJS
- [class-validator](../../backend/api/class-validator.md) — the NestJS equivalent of Data Annotations
- [FastAPI](../python/fastapi.md) — the Python framework Minimal APIs most closely resembles in spirit

import { cn } from "../../lib/utils";

/**
 * Skeleton — a placeholder element used while data is loading.
 *
 * Atlas preference: no perpetual animation. The design memo treats shimmer
 * as ops-dashboard chrome, not observatory voice. We render a quiet,
 * flat low-contrast surface instead, so the placeholder reads as "not yet
 * observed" rather than "loading." Motion is reserved for hover/focus.
 *
 * The `constellation` variant still keeps its own gentle breathing wash
 * for the Maps hero placeholder, since that skeleton is deliberately
 * expressive (and lives behind the animated constellation canvas anyway).
 */
function Skeleton({
  className,
  variant = "default",
  ...props
}: React.ComponentProps<"div"> & {
  variant?: "default" | "constellation";
}) {
  return (
    <div
      className={cn(
        "rounded-md",
        variant === "default" && "bg-muted/45",
        variant === "constellation" &&
          "skeleton-signal glass-subtle border border-primary/10",
        className
      )}
      data-slot="skeleton"
      {...props}
    />
  );
}

export { Skeleton };

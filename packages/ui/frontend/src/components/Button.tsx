import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "plain";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  icon?: ReactNode;
}

export function Button({ variant = "secondary", icon, children, className, ...props }: ButtonProps) {
  const classes = ["button", `button-${variant}`, children ? "" : "button-icon", className ?? ""];
  return (
    <button type="button" className={classes.join(" ").trim()} {...props}>
      {icon}
      {children && <span>{children}</span>}
    </button>
  );
}
